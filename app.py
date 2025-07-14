import os
import json
from dotenv import load_dotenv
from components import layout, sidebar
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ Missing OPENAI_API_KEY in .env")
    exit(1)

def load_law_sources(filepath="data/official_law_sources.json"):
    if not os.path.exists(filepath):
        print(f"❌ Law sources file not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_domain(llm_response: str, valid_domains: list[str]) -> str:
    for domain in valid_domains:
        if domain in llm_response:
            return domain
        # Fallback match ignoring spaces
        if domain.replace(" ", "") in llm_response.replace(" ", ""):
            return domain
    return None

# ========== Main ==========
def main():
    layout.render_app()
    sidebar.render_sidebar()

    # Step 1: Get User Input
    user_name, user_question = layout.render_form()
    if not user_question or not isinstance(user_question, str):
        layout.render_final_answer("❌ يرجى إدخال سؤال قانوني واضح.")
        return

    # Step 2: LLM Setup
    llm = ChatOpenAI(
        model_name="gpt-4o",
        api_key=openai_api_key,
        temperature=0.0  # Deterministic and formal
    )

    # Step 3: Domain Classification
    valid_domains = [
        "نظام العمل", "النظام الجزائي", "النظام التجاري", "الأحوال الشخصية",
        "النظام المدني", "منصة وزارة العدل", "ديوان المظالم", "المواصفات والجودة", "الهيئة العامة للعقار"
    ]
    classification_prompt = (
        f"قم بتحديد المجال القانوني المناسب للسؤال التالي باستخدام أحد هذه المجالات فقط:\n"
        f"{'، '.join(valid_domains)}\n\n"
        f"السؤال:\n{user_question}\n\n"
        f"أعد فقط اسم المجال بدقة بدون أي شرح إضافي."
    )
    raw_response = llm.invoke(classification_prompt).content
    predicted_domain = extract_domain(raw_response, valid_domains)

    if not predicted_domain:
        layout.render_final_answer("❌ لم يتم التعرف على المجال القانوني. الرجاء صياغة السؤال بشكل أوضح.")
        return

    print(f"📂 Detected Domain: {predicted_domain}")

    # Step 4: Retrieve Legal Materials
    print("🔍 Retrieving legal context from FAISS...")
    embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_db = FAISS.load_local(
        "law_vector_store",
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )

    try:
        results = vector_db.similarity_search(user_question, k=5)
    except Exception as e:
        layout.render_final_answer(f"❌ حدث خطأ أثناء البحث: {e}")
        return

    if not results:
        layout.render_final_answer("❌ لم يتم العثور على مواد قانونية ذات صلة.")
        return

    law_context = "\n\n---\n\n".join([
        f"📜 المصدر: {doc.metadata.get('source', 'غير معروف')}\n{doc.page_content}" for doc in results
    ])

    # Define the Manager Agent
    manager = Agent(
        role="Legal Consultation Manager",
        goal="Ensure the legal response is accurate, compliant with Saudi law, and understandable to the general public.",
        backstory=(
            "You are a professional Saudi lawyer responsible for overseeing the generation of legal consultations. "
            "Your job is to coordinate between the legal researcher and the legal writer to ensure the final response is accurate, well-structured, and easy to understand."
        ),
        llm=llm,
        allow_delegation=True
    )

    # Define the Researcher Agent
    researcher = Agent(
        role="Legal Researcher",
        goal="Identify and extract the legal articles most relevant to the user's question.",
        backstory=(
            f"User's Question:\n{user_question}\n\n"
            f"Legal Texts:\n{law_context}\n\n"
            f"Your task is to extract only the legal articles or clauses that are explicitly or implicitly relevant to the question. "
            f"Do not respond with 'I don't know'. Instead, use logical legal reasoning to find a connection even if it's indirect."
        ),
        llm=llm,
        allow_delegation=False
    )

    # Define the Writer Agent
    writer = Agent(
        role="Legal Response Writer",
        goal="Write a professional legal response in clear, simple Arabic that can be understood by non-lawyers.",
        backstory=(
            "Your mission is to draft a reliable legal consultation based on the provided legal materials. "
            "Start with a direct answer to the question, then explain the relevant legal background using the cited articles. "
            "Your writing must be clear, simple, and legally accurate so that any Saudi citizen without legal knowledge can understand it."
        ),
        llm=llm,
        allow_delegation=False
    )

    # Step 6: Task Definition
    task = Task(
        description=(
            f"User's Question:\n{user_question}\n\n"
            f"Legal Texts:\n{law_context}\n\n"
            f"Generate a formal legal consultation in Arabic. Start with a clear and direct answer, "
            f"then explain the legal background by citing the relevant article numbers and interpreting their content in an accessible way."
        ),
        expected_output="A legally accurate and clear Arabic response that is understandable to individuals without legal expertise.",
        agent=manager
    )

    crew = Crew(
        agents=[manager, researcher, writer],
        tasks=[task],
        verbose=True,
        memory=False
    )

    # Step 7: Run Agent Crew
    try:
        final_response = crew.kickoff()
        layout.render_final_answer(final_response)
    except Exception as e:
        layout.render_final_answer(f"❌ حدث خطأ أثناء توليد الإجابة: {e}")

# ========== Run ==========
if __name__ == "__main__":
    main()