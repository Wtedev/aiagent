from __future__ import annotations
import os, functools, asyncio
from concurrent.futures import ThreadPoolExecutor

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
vector_db = FAISS.load_local(
    VECTOR_STORE_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

_executor = ThreadPoolExecutor(max_workers=4)


# --------------------------------------------------------

async def run_chat(question: str, k: int = 20) -> str:
    docs = vector_db.similarity_search(question, k=k)
    crew = create_crew(llm, question, docs)


    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, crew.kickoff)

    if isinstance(result, str):
        return result
    if hasattr(result, "raw"):
        return result.raw                      

    if isinstance(result, list) and result:
        last = result[-1]
        return getattr(last, "raw", str(last))

   
    return result.raw.strip()
async def run_chat_stream(question: str, k: int = 20):

    docs = vector_db.similarity_search(question, k=k)
    crew = create_crew(llm, question, docs)

    answer = await run_chat(question, k)
    yield answer

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