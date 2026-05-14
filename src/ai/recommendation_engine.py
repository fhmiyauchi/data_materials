import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CHROMA_DIR = os.path.join(DATA_DIR, ".chromadb")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "materials_semantic")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

class RecommendationEngine:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path=CHROMA_DIR)
            self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
            self.collection = self.client.get_collection(name=COLLECTION_NAME, embedding_function=self.ef)
        except Exception as e:
            print(f"Failed to initialize RecommendationEngine. Error: {e}")
            self.collection = None

    def compute_custom_score(self, metadata: dict, weights: dict) -> float:
        """
        Re-calculates the composite score based on dynamic weights.
        """
        bg = metadata.get("band_gap", 0.0)
        
        # conductivity_score logic from Phase 1
        conductivity_score = max(0, 1.0 - abs(bg - 1.5) / 17.89)
        
        # stability_score is already in metadata
        stability_score = metadata.get("stability_score", 0.0)
        
        # density_score
        density = metadata.get("density", 0.0)
        density_score = max(0, 1.0 - (density / 26.58))
        
        # cost_score
        rel_cost = metadata.get("relative_cost_index", 1.0)
        cost_score = max(0, 1.0 - rel_cost)

        w_cond = weights.get("conductivity", 0.3)
        w_stab = weights.get("stability", 0.3)
        w_dens = weights.get("density", 0.2)
        w_cost = weights.get("cost", 0.2)
        
        # Normalize weights
        total_w = w_cond + w_stab + w_dens + w_cost
        if total_w > 0:
            w_cond /= total_w
            w_stab /= total_w
            w_dens /= total_w
            w_cost /= total_w

        return (
            w_cond * conductivity_score +
            w_stab * stability_score +
            w_dens * density_score +
            w_cost * cost_score
        )

    def recommend(self, query: str, weights: dict, filters: dict = None, top_k: int = 10):
        """
        Hybrid retrieval:
        1. Query ChromaDB for top matches.
        2. Apply any hard metadata filters.
        3. Re-rank the remaining candidates using the custom composite score.
        4. Return top_k.
        """
        if not self.collection:
            return []

        chroma_k = max(50, top_k * 3) # fetch more to allow re-ranking to bubble up better matches
        
        # We need to handle cases where filters might result in no items if we don't fetch enough,
        # but ChromaDB applies 'where' filters before limiting to 'n_results'.
        results = self.collection.query(
            query_texts=[query],
            n_results=chroma_k,
            where=filters # ChromaDB where clause e.g. {"is_metal": False}
        )

        if not results['documents'] or not results['documents'][0]:
            return []

        candidates = []
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i]
            id = results['ids'][0][i]
            
            custom_score = self.compute_custom_score(meta, weights)
            
            candidates.append({
                "id": id,
                "formula": meta.get("formula"),
                "description": doc,
                "metadata": meta,
                "semantic_distance": dist,
                "scientific_score": custom_score
            })
            
        # Sort by scientific score descending
        candidates.sort(key=lambda x: x["scientific_score"], reverse=True)
        
        return candidates[:top_k]

if __name__ == "__main__":
    engine = RecommendationEngine()
    
    query = "lightweight conductive material"
    weights = {"conductivity": 0.5, "stability": 0.3, "density": 0.4, "cost": 0.0}
    filters = {"is_metal": False}
    
    print(f"Testing Recommendation Engine with query: '{query}'")
    results = engine.recommend(query, weights, filters, top_k=3)
    
    for i, res in enumerate(results):
        print(f"Rank {i+1}: {res['formula']} (Score: {res['scientific_score']:.3f}, Dist: {res['semantic_distance']:.3f})")
