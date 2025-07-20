
from langchain_openai import ChatOpenAI
import os

valid_domains = [
    "نظام العمل", "النظام الجزائي", "النظام التجاري", "الأحوال الشخصية",
    "النظام المدني", "منصة وزارة العدل", "ديوان المظالم", "المواصفات والجودة", "الهيئة العامة للعقار"
]

def extract_domain(llm_response: str, valid_domains: list[str]) -> str:
    for domain in valid_domains:
        if domain in llm_response:
            return domain
        if domain.replace(" ", "") in llm_response.replace(" ", ""):
            return domain
    return None

def classify_domain(user_question: str) -> str:
    llm = ChatOpenAI(
        model_name="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.0
    )
    classification_prompt = (
        f"قم بتحديد المجال القانوني المناسب للسؤال التالي باستخدام أحد هذه المجالات فقط:\n"
        f"{', '.join(valid_domains)}\n\n"
        f"السؤال:\n{user_question}\n\n"
        f"أعد فقط اسم المجال بدقة بدون أي شرح إضافي."
    )
    response = llm.invoke(classification_prompt).content
    return extract_domain(response, valid_domains)
