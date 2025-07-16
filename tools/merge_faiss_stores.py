from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

base_store = FAISS.load_local("law_vector_store", embeddings=embedding_model,allow_dangerous_deserialization=True
)
lolo_store = FAISS.load_local("law_vector_store_lolo", embeddings=embedding_model,allow_dangerous_deserialization=True
)


print("🔀 دمج القاعدتين...")
base_store.merge_from(lolo_store)

print("💾 حفظ القاعدة الجديدة...")
base_store.save_local("law_vector_store")
print("✅ تمت العملية بنجاح. القاعدة الموحدة الآن محدثة.")
