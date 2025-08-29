import json
import openai
import math
import os
from openai import OpenAI
import gc

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_database(database_path: str="data/cases.jsonl", max_items: int=None):
    database = []
    try:
        with open(database_path, encoding="utf8") as f:
            for line in f:
                if line.strip() == "":
                    continue
                rec = json.loads(line)
                database.append({
                    "case_id": rec["case_id"],
                    "summaryOfCase": rec["summaryOfCase"],
                    "whole_case": rec.get("whole_case", {})
                })
        return database if not max_items else database[:max_items]
    except Exception as e:
        print(f"Error loading database: {e}")
        return []



agent_phase1 = """
أنت مختص قانوني سعودي تبحث في قضايا قانونية سعودية.
سيتم تزويدك بقائمة قضايا تحتوي على case_id وملخص موجز لكل قضية.
سيقدم المستخدم تفاصيل قضية تخصه مهمتك ترجع قائمة بالقضايا المشابهة مع ذكر سبب التشابه.
صيغة الإخراج يجب أن تكون JSON فقط:
[{"case_id": 1, "PointOfSimilarity": "السبب"}]
"""

agent_phase2 = """
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



llm = OpenAI(api_key=OPENAI_API_KEY or "")

def fetch_openai_chat(context, input):
    response = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": input}
        ],
        temperature=0.5,
        max_tokens=2000
    )
    return response.choices[0].message.content

def init_model():
    return {
        "phase1": {
            "system": agent_phase1
        },
        "phase2": {
            "system": agent_phase2
        }
    }



def find_matching_cases(initial_stage_model, case_data, query, batch_size=100, wait_timeout=3, progress=None):
    matching_cases  = []
    total_batches = math.ceil(len(case_data) / batch_size)

    for i in range(total_batches):
        batch = case_data[i*batch_size:(i+1)*batch_size]
        specfic_input = json.dumps([
            {"case_id": rec["case_id"], "summaryOfCase": rec["summaryOfCase"]} for rec in batch
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
            matching_cases  += json.loads(content)
        except Exception as e:
            print("Error response:", e)
        if progress:
            progress.value += 1
    return matching_cases




def generate_final_judgment(final_stage_model, case_input, matched_cases):
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

# 🚀 ADDING THE MISSING FUNCTION: run_virtual_agents
def run_virtual_agents(user_query: str):
    """
    Main function to run the virtual ruling system - EXACTLY as in test.py
    This function orchestrates the two-phase process:
    1. Find similar cases
    2. Generate final judgment
    """
    try:
        # Initialize the model (same as test.py)
        model = init_model()
        
        # Load the database (same as test.py) - 🚨 MEMORY OPTIMIZATION: Limit to 100 cases
        database = load_database(max_items=100)
        
        if not database:
            return {"error": "Failed to load case database"}
        
        # Phase 1: Find matching cases (same as test.py)
        print("🔄 Searching for similar cases...")
        matched_cases = find_matching_cases(model["phase1"], database, user_query)
        
        if not matched_cases:
            return {"error": "No similar cases found"}
        
        # Phase 2: Generate final judgment (same as test.py)
        print("⏳ Generating final judgment...")
        case_input = {"description": user_query.strip()}
        judgment = generate_final_judgment(model["phase2"], case_input, matched_cases)
        
        if not judgment:
            return {"error": "Failed to generate judgment"}
        
        # 🚨 FIX: Create proper similar_cases with summaries (EXACTLY as in test.py)
        similar_cases_with_summaries = []
        for case in matched_cases:
            case_id = case.get('case_id', 'N/A')
            # Find the full case data from database
            full_case = next((c for c in database if str(c.get('case_id')) == str(case_id)), None)
            
            if full_case:
                summary = full_case.get('summaryOfCase', 'لا يوجد ملخص متاح')
                # Create summary like in test.py
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
        
        # 🚨 MEMORY OPTIMIZATION: Force cleanup
        del database
        del matched_cases
        gc.collect()
        
        # Return the complete result (same structure as test.py)
        return {
            "similar_cases": similar_cases_with_summaries,
            "Source": judgment.get("Source", ""),
            "predicted_judgment": judgment.get("predicted_judgment", "")
        }
        
    except Exception as e:
        print(f"Error in run_virtual_agents: {e}")
        # 🚨 MEMORY OPTIMIZATION: Force cleanup on error
        gc.collect()
        return {"error": f"Failed to process request: {str(e)}"}





