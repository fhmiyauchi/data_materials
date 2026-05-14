import os
import pandas as pd
from sqlalchemy import create_engine
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "materials.db")
CHROMA_DIR = os.path.join(DATA_DIR, ".chromadb")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "materials_semantic")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

def main():
    print("Connecting to SQLite database...")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    try:
        df = pd.read_sql("SELECT * FROM material_features", engine)
    except Exception as e:
        print(f"Failed to read material_features table. Did you run build_ai_dataset.py first? Error: {e}")
        return

    print(f"Loaded {len(df)} materials from feature table.")

    # Convert NaNs in metadata to None (or proper types) so ChromaDB accepts them
    df = df.where(pd.notnull(df), None)

    print(f"Initializing ChromaDB at {CHROMA_DIR}...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # We will use sentence-transformers locally (fast and free)
    # The default for ChromaDB is all-MiniLM-L6-v2, which is perfect for this MVP.
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    # Re-create the collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass
    
    print(f"Creating collection '{COLLECTION_NAME}'...")
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)

    print("Preparing documents for ingestion...")
    documents = df["feature_text"].tolist()
    ids = df["material_id"].tolist()
    
    # Extract metadata mapping
    metadata = []
    for _, row in df.iterrows():
        # ChromaDB metadata can only be str, int, float, or bool
        meta = {
            "formula": str(row["formula"]),
            "density": float(row["density"]) if row["density"] is not None else 0.0,
            "band_gap": float(row["band_gap"]) if row["band_gap"] is not None else 0.0,
            "stability_score": float(row["stability_score"]),
            "relative_cost_index": float(row["relative_cost_index"]),
            "crystal_system": str(row["crystal_system"]),
            "is_metal": bool(row["is_metal"]),
        }
        metadata.append(meta)

    print(f"Embedding and storing {len(documents)} documents in ChromaDB... (this may take a minute or two)")
    
    # Batch ingestion
    batch_size = 1000
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        print(f"  -> Ingesting batch {i} to {end_idx}...")
        collection.add(
            documents=documents[i:end_idx],
            metadatas=metadata[i:end_idx],
            ids=ids[i:end_idx]
        )

    print("Vector store populated successfully!")
    print(f"Total documents in collection: {collection.count()}")

if __name__ == "__main__":
    main()
