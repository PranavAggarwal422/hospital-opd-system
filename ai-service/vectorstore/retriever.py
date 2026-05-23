from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

COLLECTION_NAME = "hospital_portal_kb"
PERSIST_DIRECTORY = "vectorstore/chroma_db"

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embedding_model,
    collection_name=COLLECTION_NAME,
    collection_metadata={"hnsw:space": "cosine"}
)


def retrieve_context(query: str, top_k: int = 4):
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    relevant_docs = retriever.invoke(query)
    if not relevant_docs:
        return ""
    
    contexts = []

    for doc in relevant_docs:
        section = doc.metadata.get("section", "UNKNOWN_SECTION")
        contexts.append(f"[{section}]\n{doc.page_content}")

    return "\n\n".join(contexts)

