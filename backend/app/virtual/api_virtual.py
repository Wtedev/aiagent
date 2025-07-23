
import json
import math
import os
from openai import OpenAI

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
مهتمتك هو تقديم حكم نهائي باللغة العربية لقضية المستخدم مع شرح قصير وادعم حكمك بدلائل من القضايا المشابهة.
الإخراج يجب أن يكون JSON فقط:
{
  "similar_cases": [{"case_id": 15, "summary": " نبذة قصيرة حول هذه القضية"}],
  "Source": "اشرح شرح قصير كيف ساعدتك القضاياالمتشابهة في اصدار حكم لقضية اليوزر"
  "predicted_judgment": " نص الحكم المتوقع لقضية اليوزر"
}
"""



llm = OpenAI(api_key="")

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
        "phase1": {"system": agent_phase1},
        "phase2": {"system": agent_phase2}
    }

def find_matching_cases(initial_stage_model, case_data, query, batch_size=100):
    matching_cases = []
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
def run_virtual_agents(user_query, database_path="data/cases.jsonl"):
    model = init_model()
    cases = load_database(database_path)
# Phase 1: Find matching cases
    matches = find_matching_cases(model["phase1"], cases, user_query)
# Phase 2: Build similar cases summaries
    similar_cases = []
    for match in matches[:5]:  # Take top 5 matches
        cid = match.get("case_id")
        for case in cases:
            if case["case_id"] == cid:
                # Compose summary for phase 2
                summary = (case.get("summaryOfCase", {}).get("summary") or [""])[0]
                similar_cases.append({"case_id": cid, "summary": summary})
    # Phase 2: Final judgment
    final_result = generate_final_judgment(
        model["phase2"],
        case_input=user_query,     
        matched_cases=similar_cases
    )
    return final_result

