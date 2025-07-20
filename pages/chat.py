# chat.py

import os
from dotenv import load_dotenv
from app.tasks import create_crew
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from components import layout
import streamlit as st

# ───────────────────────────────────────────────────────
# Load environment variables and models
load_dotenv()

st.markdown("""
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-4o",
    api_key=openai_api_key,
    temperature=0.0
)

embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

VECTOR_STORE_PATH = "data/law_vector_store"
vector_db = FAISS.load_local(
    VECTOR_STORE_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# ───────────────────────────────────────────────────────
def extract_answer(result):
    if isinstance(result, dict) and "raw" in result:
        return result["raw"]
    elif hasattr(result, "raw"):
        return result.raw
    elif hasattr(result, "output") and isinstance(result.output, str):
        return result.output
    return None  # return None instead of str(result)

# ───────────────────────────────────────────────────────
def main():
    layout.render_app()
    st.title("💬 المساعد القانوني الذكي")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render previous messages
    for msg in st.session_state.chat_history:
        layout.chat_message(msg["role"], msg["content"])

    # Get user input
    user_question = st.chat_input("🖊️ أدخل سؤالك القانوني هنا...")

    if not user_question:
        return

    # Display user message
    layout.chat_message("user", user_question)
    st.session_state.chat_history.append({"role": "user", "content": user_question})

    # ───── Step 1: Search Context ─────
    try:
        docs_with_scores = vector_db.similarity_search_with_score(user_question, k=10)
        top_docs = [doc for doc, score in docs_with_scores]
    except Exception as e:
        error = f"❌ خطأ أثناء استرجاع النصوص القانونية: {e}"
        layout.chat_message("assistant", error)
        st.session_state.chat_history.append({"role": "assistant", "content": error})
        return

    if not top_docs:
        warning = "⚠️ لم يتم العثور على نص قانوني مشابه للسؤال المطروح."
        layout.chat_message("assistant", warning)
        st.session_state.chat_history.append({"role": "assistant", "content": warning})
        return

    context = "\n\n---\n\n".join([
        f"📜 المصدر: {doc.metadata.get('source', 'غير معروف')}\n{doc.page_content}"
        for doc in top_docs[:5]
    ])

    # ───── Step 2: Run Crew with Spinner ─────
    with st.spinner("⏳ جاري توليد الإجابة القانونية..."):
        try:
            crew = create_crew(llm=llm, user_question=user_question, law_context=context)
            result = crew.kickoff()
            st.session_state.last_full_response = result
            final_answer = extract_answer(result)
        except Exception as e:
            final_answer = None
            error_msg = f"❌ حدث خطأ أثناء توليد الإجابة: {e}"
            layout.chat_message("assistant", error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            return

    # ✅ Only show assistant message if it's valid
    if final_answer and final_answer.strip().lower() != "undefined":
        layout.chat_message("assistant", final_answer)
        st.session_state.chat_history.append({"role": "assistant", "content": final_answer})
    else:
        fallback_msg = "⚠️ لم يتم التوصل إلى إجابة واضحة لهذا السؤال حالياً."
        layout.chat_message("assistant", fallback_msg)
        st.session_state.chat_history.append({"role": "assistant", "content": fallback_msg})

# ───────────────────────────────────────────────────────
if __name__ == "__main__":
    main()