import os
import re

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

def load_documents(docs_path):
    """Load all text files from the specified directory and return as a list of Document objects"""
    print(f"Loading documents from {docs_path}...")
    
    # Check if docs directory exists
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist.")
    
    # Load all .txt files from the docs directory
    loader = DirectoryLoader(path=docs_path, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if len(documents) == 0:
        raise FileNotFoundError(f"No .txt files found in {docs_path}")

    return documents

def split_by_sections(document):
    """Split document using [SECTION_NAME] headings."""
    pattern = r"\[(.*?)\]"
    matches = list(re.finditer(pattern, document.page_content))

    chunks = []

    for i in range(len(matches)):
        start = matches[i].start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(document.page_content)

        chunk_text = document.page_content[start:end].strip()
        section_title = matches[i].group(1)

        chunks.append(
            Document(
                page_content=chunk_text,
                metadata={
                    "source": document.metadata["source"],
                    "section": section_title
                }
            )
        )
    
    if chunks:
        for i, chunk in enumerate(chunks[:5]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Source: {chunk.metadata['source']}")
            print(f"Length: {len(chunk.page_content)} characters")
            print(f"Content:")
            print(chunk.page_content)
            print("-" * 50)
        
        if len(chunks) > 5:
            print(f"\n... and {len(chunks) - 5} more chunks")
    
    return chunks

def build_chunks(documents):
    """
    Convert documents into structured chunks.
    """
    all_chunks = []

    for doc in documents:
        chunks = split_by_sections(doc)
        all_chunks.extend(chunks)

    return all_chunks


def create_vector_store(chunks, persist_directory="db/chroma_db"):
    """Create and persist ChromaDB vector store"""
    print("Creating embeddings and storing in ChromaDB...")
 
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create ChromaDB vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory, 
        collection_name="hospital_portal_kb",
        collection_metadata={"hnsw:space": "cosine"}
    )

    print(f"Vector store created and saved to {persist_directory}")
    return vectorstore

def main():
    docs_path = "../data"
    persistent_directory = "./chroma_db"

    try : 
        # Check if vector store already exists
        if os.path.exists(persistent_directory):
            print("Vector store already exists. No need to re-process documents.")
            
            embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vectorstore = Chroma(
                persist_directory=persistent_directory,
                embedding_function=embedding_model, 
                collection_name="hospital_portal_kb",
                collection_metadata={"hnsw:space": "cosine"}
            )

            print(f"Loaded existing vector store with {vectorstore._collection.count()} chunks")
            return vectorstore
        
        print("Persistent directory does not exist. Initializing vector store...\n")
        
        # Load documents
        documents = load_documents(docs_path)  

        # Split into chunks
        chunks = build_chunks(documents)
        
        # Create vector store
        vectorstore = create_vector_store(chunks, persistent_directory)
        
        print("\nIngestion complete!")
        print(f"Stored {vectorstore._collection.count()} chunks.")
        return vectorstore
    
    except Exception as e:
        print(f"Error during ingestion: {str(e)}")
        raise


if __name__ == "__main__":
    main()

