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
                db.append({
                    "case_id": rec.get("case_id"),
                    "summaryOfCase": rec.get("summaryOfCase", ""),
                    "whole_case": rec.get("whole_case", {}),
                })
        return db if not max_items else db[:max_items]
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

AGENT_PHASE1 = """
أنت مختص قانوني سعودي تبحث في قضايا قانونية سعودية.
سيتم تزويدك بقائمة قضايا تحتوي على case_id وملخص موجز لكل قضية.
سيقدم المستخدم تفاصيل قضية تخصه. مهمتك: ارجع قائمة بالقضايا المشابهة مع سبب التشابه.
أعد JSON صالح فقط بشكل:
[{"case_id": 1, "PointOfSimilarity": "السبب"}]
"""

AGENT_PHASE2 = """
أنت مختص قانوني سعودي. سيتم تزويدك بتفاصيل قضية المستخدم، إضافة إلى القضايا المشابهة.
أعد JSON فقط بالمفاتيح:
1) "similar_cases": [{"case_id": 15,"summary": "ملخص < 50 كلمة + فكرة الحكم"}]
2) "Source": كيف ساعدتك القضايا المشابهة.
3) "predicted_judgment": الحكم الشرعي الرسمي المفصل.
"""

def init_model() -> Dict[str, Dict[str, str]]:
    return {"phase1": {"system": AGENT_PHASE1}, "phase2": {"system": AGENT_PHASE2}}

def find_matching_cases(initial_stage_model: Dict[str, str], case_data: List[Dict[str, Any]], query: str, batch_size: int = 100) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    total_batches = math.ceil(len(case_data) / batch_size)
    for i in range(total_batches):
        batch = case_data[i * batch_size : (i + 1) * batch_size]
        batch_json = json.dumps(
            [{"case_id": r.get("case_id"), "summaryOfCase": r.get("summaryOfCase", "")} for r in batch],
            ensure_ascii=False,
            indent=2,
        )
        user_input = f"""
# القضايا المدخلة
```json
{batch_json}
```

القضية التي سنقارنها

{query}

أعد JSON صالح فقط
"""
        try:
            content = fetch_openai_chat(initial_stage_model["system"], user_input)
            content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)
            if isinstance(parsed, list):
                out.extend(parsed)
        except Exception as e:
            print("Error response:", e)
    return out

def generate_final_judgment(final_stage_model: Dict[str, str], case_input: Dict[str, Any], matched_cases: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    case_json = json.dumps(case_input, ensure_ascii=False, indent=2)
    matched_json = json.dumps(matched_cases, ensure_ascii=False, indent=2)
    user_input = f"""
تفاصيل القضية:

{case_json}

القضايا المشابهة:

{matched_json}

أعد JSON صالح فقط
"""
    try:
        content = fetch_openai_chat(final_stage_model["system"], user_input)
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print("Error judgment:", e)
        return None

def _to_str_query(user_query: Any) -> str:
    # Normalize any payload (dict/list/str) into a clean string for LLM
    if isinstance(user_query, str):
        return user_query.strip()
    try:
        return json.dumps(user_query, ensure_ascii=False)
    except Exception:
        return str(user_query)

def run_virtual_agents(user_query: Any) -> Dict[str, Any]:
    """
    Orchestrates:
    1) similar-case lookup
    2) final judgment generation
    – hardened against unhashable/slice errors by normalizing input.
    """
    try:
        model = init_model()
        database = load_database(max_items=100)
        if not database:
            return {"error": "Failed to load case database"}

        query_str = _to_str_query(user_query)
        print("🔄 Searching for similar cases...")
        matched = find_matching_cases(model["phase1"], database, query_str)

        if not matched:
            return {"error": "No similar cases found"}

        print("⏳ Generating final judgment...")
        case_input = {"description": query_str}
        judgment = generate_final_judgment(model["phase2"], case_input, matched)
        if not judgment:
            return {"error": "Failed to generate judgment"}

        # Optional enrichment of similar cases with short summaries
        similar_cases_with_summaries: List[Dict[str, Any]] = []
        db_index = {str(x.get("case_id")): x for x in database}
        for m in matched:
            cid = str(m.get("case_id"))
            base = db_index.get(cid)
            if base:
                summary = base.get("summaryOfCase", "")
                short = summary[:50] + ("..." if len(summary) > 50 else "")
                similar_cases_with_summaries.append({
                    "case_id": cid,
                    "summary": short or "لا يوجد ملخص متاح",
                    "PointOfSimilarity": m.get("PointOfSimilarity", "غير محدد"),
                })

        del database, matched
        gc.collect()

        return {
            "similar_cases": similar_cases_with_summaries or judgment.get("similar_cases", []),
            "Source": judgment.get("Source", ""),
            "predicted_judgment": judgment.get("predicted_judgment", ""),
        }
    except Exception as e:
        print(f"Error in run_virtual_agents: {e}")
        gc.collect()
        return {"error": f"Failed to process request: {str(e)}"}
