from __future__ import annotations
import os, functools, asyncio
from concurrent.futures import ThreadPoolExecutor
import gc
import warnings

# 🚨 SUPPRESS SWIG warnings from faiss-cpu
warnings.filterwarnings("ignore", category=DeprecationWarning, module="importlib._bootstrap")

from backend.app.roadmap.roadmap_agents import create_roadmap_crew
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from backend.app.chatbot.tasks import create_crew        

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH")

llm = ChatOpenAI( 
    model_name="gpt-4o",
    api_key=OPENAI_API_KEY,
    temperature=0.0
) 

embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Load FAISS vector store directly
print("🔄 Loading FAISS vector store...")
vector_db = FAISS.load_local(
    VECTOR_STORE_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)
print("✅ FAISS vector store loaded successfully")

_executor = ThreadPoolExecutor(max_workers=4)

# --------------------------------------------------------

async def run_chat(question: str, k: int = 10) -> str:  # 🚨 REDUCE from k=20 to k=10
    try:
        docs = vector_db.similarity_search(question, k=k)
        
        # 🚨 SIMPLIFIED: Use direct LLM instead of CrewAI to avoid errors
        try:
            crew = create_crew(llm, question, docs)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(_executor, crew.kickoff)

            if isinstance(result, str):
                return result
            if hasattr(result, "raw"):
                return result.raw                       # CrewOutput.raw

            if isinstance(result, list) and result:
                last = result[-1]
                return getattr(last, "raw", str(last))

            # fallback أخير
            if hasattr(result, "raw"):
                return result.raw.strip()
            else:
                return str(result)
                
        except Exception as crew_error:
            print(f"CrewAI failed, falling back to direct LLM: {crew_error}")
            # 🚨 FALLBACK: Direct LLM approach if CrewAI fails
            fallback_prompt = f"""
            أنت مستشار قانوني سعودي متخصص. أجب على السؤال التالي باللغة العربية:
            
            السؤال: {question}
            
            أجب بطريقة واضحة ومفيدة، مع الاستشهاد بالقوانين السعودية إذا أمكن.
            """
            
            response = llm.invoke(fallback_prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
    except Exception as e:
        print(f"Error in run_chat: {e}")
        return f"عذراً، حدث خطأ أثناء معالجة سؤالك: {str(e)}"
    finally:
        # 🚨 MEMORY OPTIMIZATION: Force cleanup
        gc.collect()

async def run_chat_stream(question: str, k: int = 20):
    docs = vector_db.similarity_search(question, k=k)
    crew = create_crew(llm, question, docs)
    answer = await run_chat(question, k)
    yield answer

async def run_roadmap(question: str, k: int = 20) -> str:
    docs = vector_db.similarity_search(question, k=k)
    crew = create_roadmap_crew(llm, question, docs)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, crew.kickoff)

    if isinstance(result, str):
        return result
    if hasattr(result, "raw"):              # CrewOutput
        return result.raw
    return str(result)