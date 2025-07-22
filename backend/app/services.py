from __future__ import annotations
import os, functools, asyncio
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from backend.app.tasks import create_crew           # يتوقع (llm, user_question, law_context)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH")

# ➊ ثبّت نموذج  LLM واحد (يمكنك تغيير الإعدادات كما تريد)
llm = ChatOpenAI( 
    model_name="gpt-4o",
    api_key=OPENAI_API_KEY,
    temperature=0.0
) 

# ➋ حمّل قاعدة المتجهات مرة واحدة
embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_db = FAISS.load_local(
    VECTOR_STORE_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# Executor لإبعاد العمل الحظري عن لوب FastAPI
_executor = ThreadPoolExecutor(max_workers=4)


# --------------------------------------------------------

async def run_chat(question: str, k: int = 5) -> str:
    # … اختيار السياق وبناء الـ crew كما هو …
    docs = vector_db.similarity_search(question, k=k)
    law_context = "\n\n".join(d.page_content for d in docs)
    crew = create_crew(llm, question, law_context)


    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, crew.kickoff)

    # 🔽 حوِّل الأنواع غير النصية إلى نص
    if isinstance(result, str):
        return result
    if hasattr(result, "raw"):
        return result.raw                       # CrewOutput.raw
    # إذا كان قائمة TaskOutput خذ الأخير
    if isinstance(result, list) and result:
        last = result[-1]
        return getattr(last, "raw", str(last))

    # fallback أخير
    return str(result)
async def run_chat_stream(question: str, k: int = 5):
    """
    مولّد Async يبث الرد تدريجيًا (إذا كان Crew أو الـ LLM يدعم ذلك).
    """
    docs = vector_db.similarity_search(question, k=k)
    law_context = "\n\n".join(d.page_content for d in docs)

    crew = create_crew(llm, question, law_context)

    # إن لم يكن لديك stream حقيقي يمكنك إعادة النتيجة دفعة واحدة
    answer = await run_chat(question, k)
    yield answer