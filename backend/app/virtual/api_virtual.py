import json
import math
import os
import gc
from typing import Any, Dict, List

from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY or "")

def fetch_openai_chat(system_prompt: str, user_input: str) -> str:
    resp = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.5,
        max_tokens=2000,
    )
    return resp.choices[0].message.content

def load_database(database_path: str = "data/cases.jsonl", max_items: int | None = None) -> List[Dict[str, Any]]:
    db: List[Dict[str, Any]] = []
    try:
        with open(database_path, encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                # Convert Arabic numerals to regular numbers and ensure case_id is a string
                case_id = rec.get("case_id")
                if case_id is not None:
                    # Convert Arabic numerals to regular numbers
                    arabic_to_english = {
                        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
                    }
                    case_id_str = str(case_id)
                    for arabic, english in arabic_to_english.items():
                        case_id_str = case_id_str.replace(arabic, english)
                    case_id = case_id_str
                
                # Handle summaryOfCase properly - it's a dict, extract the summary
                summary_of_case = rec.get("summaryOfCase", "")
                if isinstance(summary_of_case, dict):
                    # Extract summary from the dict
                    summary = summary_of_case.get("summary", "")
                    if isinstance(summary, list):
                        summary = " ".join(summary)
                    elif not isinstance(summary, str):
                        summary = str(summary)
                else:
                    summary = str(summary_of_case)
                
                db.append({
                    "case_id": case_id,
                    "summaryOfCase": summary,
                    "whole_case": rec.get("whole_case", {}),
                })
        return db if not max_items else db[:max_items]
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

AGENT_PHASE1 = """
أنت مختص قانوني سعودي تبحث في قضايا قانونية سعودية.
سيتم تزويدك بقائمة قضايا تحتوي على case_id وملخص موجز لكل قضية.
سيقدم المستخدم تفاصيل قضية تخصه مهمتك ترجع قائمة بالقضايا المشابهة مع ذكر سبب التشابه.
صيغة الإخراج يجب أن تكون JSON فقط:
[{"case_id": 1, "PointOfSimilarity": "السبب"}]
"""

AGENT_PHASE2 = """
أنت مختص قانوني سعودي. سيتم تزويدك بقضية مع كامل تفاصيلها، بالإضافة إلى مجموعة قضايا مشابهة.
مهمتك إصدار حكم نهائي مفصل لقضية المستخدم، ويجب أن يشمل الإخراج JSON يحتوي على المفاتيح التالية:

1. "similar_cases": قائمة من القضايا المتشابهة بصيغة:
   [{"case_id": 15,"summary": "ملخص اقل من 50 كلمة يصف وقائع القضية، متبوعًا بملخص مختصر لحكم القاضي في هذه القضية (فكرة الحكم أو النتيجة الرئيسية فقط، بدون تفاصيل مطولة)."}]

2. "Source": شرح قصير يوضح كيف ساعدتك القضايا المشابهة في إصدار الحكم (بالعربية وبأسلوب واضح).

3. "predicted_judgment": النص الكامل للحكم الشرعي الرسمي، ويجب أن يكون مفصلًا ويُكتب كأنك قاضٍ شرعي بالمملكة العربية السعودية، مع اتباع النقاط التالية:

- ابدأ بمقدمة شرعية مثل: "الحمد لله وحده، والصلاة والسلام على من لا نبي بعده، وبعد:"
- يجب عليك الاستشهاد إلى الأنظمة الشرعية والنظامية، والأحاديث والآيات المناسبة.
- صِغ منطوق الحكم مفصلًا وبالترتيب (أولًا، ثانيًا، ثالثًا...).
- اشرح شرح قصير كيف ساعدتك القضاياالمتشابهة في اصدار حكم لقضية اليوزر"
- اختم الحكم بصيغة رسمية مثل: "والله الموفق، وصلى الله على نبينا محمد وعلى آله وصحبه وسلم أجمعين."
- لا تستخدم قوالب جاهزة أو عبارات مكررة، بل اجعل الحكم خاصًا بالقضية.
{

}
الآن، هذه تفاصيل القضية:
{case_details}

وهذه القضايا المشابهة المرجعية:
{similar_cases}

أخرج النتيجة بصيغة JSON فقط تتضمن المفاتيح الثلاثة المذكورة أعلاه.
"""

def init_model() -> Dict[str, Dict[str, str]]:
    return {
        "phase1": {
            "system": AGENT_PHASE1
        },
        "phase2": {
            "system": AGENT_PHASE2
        }
    }

def find_matching_cases(initial_stage_model: Dict[str, str], case_data: List[Dict[str, Any]], query: str, batch_size: int = 100, wait_timeout: int = 3, progress=None) -> List[Dict[str, Any]]:
    matching_cases = []
    total_batches = math.ceil(len(case_data) / batch_size)

    for i in range(total_batches):
        batch = case_data[i * batch_size:(i + 1) * batch_size]
        specfic_input = json.dumps([
            {"case_id": rec.get("case_id"), "summaryOfCase": rec.get("summaryOfCase", "")} for rec in batch
        ], ensure_ascii=False, indent=2)

        user_input = f"""
# القضايا المدخلة
```json
{specfic_input}
```
# القضية التي سنقارنها
{query}
# قم بارجاع jsonصحيح فقط
"""

        try:
            content = fetch_openai_chat(initial_stage_model["system"], user_input)
            content = content.replace("```json", "").replace("```", "").strip()
            parsed_content = json.loads(content)
            if isinstance(parsed_content, list):
                matching_cases.extend(parsed_content)
            else:
                print(f"Unexpected response format: {type(parsed_content)}")
        except Exception as e:
            print("Error response:", e)
        if progress:
            progress.value += 1
    return matching_cases

def generate_final_judgment(final_stage_model: Dict[str, str], case_input: Dict[str, Any], matched_cases: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    input_json = json.dumps(case_input, ensure_ascii=False, indent=2)
    matched_json = json.dumps(matched_cases, ensure_ascii=False, indent=2)

    user_input = f"""
# تفاصيل القضية:
{input_json}
# القضايا المشابهة:
{matched_json}
# رجاءً أعد فقط JSON صحيح
"""
    try:
        content = fetch_openai_chat(final_stage_model["system"], user_input)
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print("Error judgment:", e)
        return None

def run_virtual_agents(user_query: str) -> Dict[str, Any]:
    """
    Main function to run the virtual ruling system - EXACTLY as in the working Streamlit code
    This function orchestrates the two-phase process:
    1. Find similar cases
    2. Generate final judgment
    """
    try:
        # Initialize the model (same as Streamlit)
        model = init_model()
        
        # Load the database (same as Streamlit)
        database = load_database()
        
        if not database:
            return {"error": "Failed to load case database"}
        
        # Phase 1: Find matching cases (same as Streamlit)
        print("🔄 Searching for similar cases...")
        matched_cases = find_matching_cases(model["phase1"], database, user_query)
        
        if not matched_cases:
            return {"error": "No similar cases found"}
        
        # Phase 2: Generate final judgment (same as Streamlit)
        print("⏳ Generating final judgment...")
        case_input = {"description": user_query.strip()}
        judgment = generate_final_judgment(model["phase2"], case_input, matched_cases)
        
        if not judgment:
            return {"error": "Failed to generate judgment"}
        
        # Create proper similar_cases with summaries (EXACTLY as in Streamlit)
        similar_cases_with_summaries = []
        for case in matched_cases:
            case_id = case.get('case_id', 'N/A')
            # Find the full case data from database
            full_case = next((c for c in database if str(c.get('case_id')) == str(case_id)), None)
            
            if full_case:
                summary = full_case.get('summaryOfCase', 'لا يوجد ملخص متاح')
                # Create summary like in Streamlit
                case_summary = f"{summary[:50]}{'...' if len(summary) > 50 else ''}"
                similar_cases_with_summaries.append({
                    "case_id": case_id,
                    "summary": case_summary,
                    "PointOfSimilarity": case.get('PointOfSimilarity', 'غير محدد')
                })
            else:
                similar_cases_with_summaries.append({
                    "case_id": case_id,
                    "summary": "لا يوجد ملخص متاح",
                    "PointOfSimilarity": case.get('PointOfSimilarity', 'غير محدد')
                })
        
        # Return the complete result (same structure as Streamlit)
        return {
            "similar_cases": similar_cases_with_summaries,
            "Source": judgment.get("Source", ""),
            "predicted_judgment": judgment.get("predicted_judgment", "")
        }
        
    except Exception as e:
        print(f"Error in run_virtual_agents: {e}")
        return {"error": f"Failed to process request: {str(e)}"}
