import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from src.ai.recommendation_engine import RecommendationEngine

load_dotenv()

class AIWorkflow:
    def __init__(self):
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-5.4-mini")
        self.llm = ChatOpenAI(model=model_name, temperature=0.0, model_kwargs={"response_format": {"type": "json_object"}}) # State of the art, fast and cost effective
        self.engine = RecommendationEngine()
        
        self.intent_prompt = PromptTemplate.from_template(
            """You are a materials science AI assistant. 
Extract the optimization intent from the user's query into JSON format.

Available weight dimensions (must sum to 1.0):
- conductivity: prioritize low band gap (or metallic properties)
- stability: prioritize thermodynamic stability (energy above hull)
- density: prioritize lightweight materials
- cost: prioritize abundant, cheap elements

Available filters:
- is_metal: true for metals, false for non-metals/semiconductors/insulators. Leave null if no preference.
- avoid_elements: list of elemental symbols to avoid (e.g. ["Co", "Ni"]).

User Query: "{query}"

Respond ONLY with valid JSON matching this exact schema:
{{
    "weights": {{"conductivity": float, "stability": float, "density": float, "cost": float}},
    "filters": {{"is_metal": bool or null, "avoid_elements": [str]}}
}}
"""
        )
        
        self.explain_prompt = PromptTemplate.from_template(
            """You are an expert materials scientist explaining a material recommendation.

User Query: "{query}"
Recommended Material: {formula}
Crystal System: {crystal_system}
Composite Score: {score}

Material Data:
- Density: {density} g/cm3
- Band Gap: {band_gap} eV
- Energy Above Hull: {stability} eV/atom (0 is perfectly stable)
- Element Rarity Index: {cost_index} (0 is cheapest, 1 is rarest)

Respond ONLY with valid JSON matching this exact schema:
{{
    "scientific_explanation": "Markdown string (3-4 bullets) explaining WHY it was recommended based on the data. Use ✅ and ⚠️.",
    "potential_usage": "Markdown string suggesting 1-2 real-world industrial/scientific applications for this material based on its properties. Use 💡."
}}
"""
        )

    def extract_intent(self, query: str) -> dict:
        prompt = self.intent_prompt.format(query=query)
        response = self.llm.invoke(prompt)
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Failed to parse LLM intent JSON: {e}. Using defaults.")
            return {
                "weights": {"conductivity": 0.25, "stability": 0.25, "density": 0.25, "cost": 0.25},
                "filters": {"is_metal": None, "avoid_elements": []}
            }

    def process_query(self, query: str):
        print("Extracting intent...")
        intent = self.extract_intent(query)
        print(f"Parsed Intent: {json.dumps(intent, indent=2)}")
        
        # Build ChromaDB filter
        chroma_filter = {}
        if intent["filters"].get("is_metal") is not None:
            chroma_filter["is_metal"] = intent["filters"]["is_metal"]
            
        print("\nRetrieving candidates...")
        # Fetch a massive pool of candidates first so that post-retrieval filters don't exhaust the list
        candidates = self.engine.recommend(
            query=query, 
            weights=intent["weights"], 
            filters=chroma_filter if chroma_filter else None,
            top_k=1000
        )
        
        if not candidates:
            return "No matching materials found.", [], intent
            
        # Optional: apply avoid_elements filter post-retrieval
        avoid = intent["filters"].get("avoid_elements", [])
        if avoid:
            from pymatgen.core import Composition
            filtered = []
            for c in candidates:
                try:
                    comp_elements = [el.symbol for el in Composition(c["formula"]).elements]
                    if not any(a in comp_elements for a in avoid):
                        filtered.append(c)
                except Exception:
                    filtered.append(c)
            candidates = filtered

        # Truncate to the top 5 valid candidates after filtering
        candidates = candidates[:5]

        if not candidates:
            return "No matching materials found after applying element filters.", [], intent

        print("\nGenerating explanations for top 3 candidates...")
        # Note: stability in metadata is energy_above_hull
        for c in candidates[:3]:
            explain_prompt = self.explain_prompt.format(
                query=query,
                formula=c["formula"],
                crystal_system=c["metadata"].get("crystal_system"),
                score=f"{c['scientific_score']:.2f}",
                density=f"{c['metadata'].get('density', 0.0):.2f}",
                band_gap=f"{c['metadata'].get('band_gap', 0.0):.2f}",
                stability=f"{c['metadata'].get('stability_score', 0.0):.3f}",
                cost_index=f"{c['metadata'].get('relative_cost_index', 1.0):.3f}"
            )
            c["explanation"] = self.llm.invoke(explain_prompt).content
        
        # We can still return the first explanation for backwards compatibility, or just let the frontend use the dict
        return candidates[0]["explanation"], candidates, intent

if __name__ == "__main__":
    import sys
    # Load .env variables so os.environ picks them up, handled by load_dotenv()
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set OPENAI_API_KEY in your .env file to run this test.")
        sys.exit(1)
        
    workflow = AIWorkflow()
    query = "Suggest safer and affordable alternatives to cobalt-based high-nickel cathodes"
    
    print(f"\nUser Query: {query}\n")
    explanation, candidates = workflow.process_query(query)
    
    print("\n" + "="*50)
    print("AI EXPLANATION:")
    print("="*50)
    print(explanation)
    
    print("\n" + "="*50)
    print("TOP CANDIDATES:")
    print("="*50)
    for i, c in enumerate(candidates[:3]):
        print(f"#{i+1}: {c['formula']} (Score: {c['scientific_score']:.3f})")
