import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CHROMA_DIR = os.path.join(DATA_DIR, ".chromadb")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "materials_semantic")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

def main():
    print(f"Connecting to ChromaDB at {CHROMA_DIR}...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)
        print(f"Successfully connected to collection. Total documents: {collection.count()}")
    except Exception as e:
        print(f"Failed to load collection '{COLLECTION_NAME}'. Did you run build_vector_store.py? Error: {e}")
        return

    query = "lightweight conductive material"
    print(f"\nExecuting test query: '{query}'")
    print("-" * 50)
    
    results = collection.query(
        query_texts=[query],
        n_results=3,
        where={"is_metal": False} # Optional metadata filter: non-metals only
    )

    if not results['documents'] or not results['documents'][0]:
        print("No results found.")
        return

    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
        print(f"Rank {i+1} (Distance: {distance:.4f})")
        print(f"Material: {metadata['formula']} (Crystal System: {metadata['crystal_system']})")
        print(f"Description: {doc}")
        print("-" * 50)

if __name__ == "__main__":
    main()
