# Task 2 — Technical Walkthrough (15 min)
## AI Material Intelligence Platform (RAG & Semantic Search)

---

## ⏱️ Time Budget

| Slide | Topic | Time |
|---|---|---|
| 1 | Title | — |
| 2 | Context & Disclaimer | 1 min |
| 3 | Real-World AI Applications in Industry | 1 min |
| 4 | Why We Chose This Path ("AI-Guru") | 1 min |
| 5 | Problem Statement & AI Vision | 1 min |
| 6 | Deliverables Planned | 30 sec |
| 7 | Architecture: Hybrid RAG System | 1.5 min |
| 8 | The Semantic Payload (Embeddings) | 1.5 min |
| 9 | AI Pipeline: Intent & Explainability | 2 min |
| 10 | Challenges, Trade-offs & Resiliency | 4 min |
| **11** | **Live Demo (Streamlit)** | **4–5 min** |
| 12 | Final Outcomes & Deliverables | 30 sec |
| **—** | **Discussion** | **15 min** |

---

## Slide 1 — Title

**Title:** Building an AI Material Intelligence Platform
**Subtitle:** LLM Intent Extraction · Vector Hybrid Search · Explainable AI
**Date:** May 2025

---

## Slide 2 — Context & Disclaimer *(~1 min)*

- 🧪 **Proof-of-concept, not production** — Architectural decisions were optimized for demonstrating rapid prototyping and technical reasoning, not operational scale.
- 🎯 **Open-ended Brief** — Because the scope was intentionally left open, we proactively ideated and built "AI-Guru" (Material Intelligence) to demonstrate a high-value, practical scientific use case.
- 📉 **Vector Sample Size** — To ensure local execution speed during the demo, ChromaDB only embedded a representative sample of the 154k material database.
- 💾 **Aggressive Caching** — The live demo uses a permanent JSON disk cache to bypass LLM execution delays and save API credits on pre-computed examples.
- 🤖 **Illustrative XAI** — The AI's scientific explanations are meant to demonstrate the pipeline's capabilities and should not be treated as verified, peer-reviewed scientific conclusions.
- 🛠️ **AI-Assisted Development** — LLMs were used for domain research acceleration and code scaffolding; all architectural decisions and reasoning are the author's own.

---

## Slide 3 — Real-World AI Applications in Industry *(~1 min)*

**Headline:** *"AI is actively transforming how industries manage and discover complex data."*

- 🧬 **Generative Design & Discovery Simulations:** Accelerating the discovery of new alloys and drugs by predicting chemical viability before physical lab testing.
- 🏭 **Digital Twins & Predictive Modeling:** Creating virtual representations of physical assets (like factory turbines) to simulate stress and predict maintenance cycles.
- 🗣️ **Text-to-SQL & Advanced Querying:** Empowering business users to query complex relational databases using natural language, without needing to know SQL.
- 🔍 **Semantic Search (RAG):** Using Vector Databases (like ChromaDB) and Large Language Models to retrieve information based on *meaning* rather than exact keyword matches.

---

## Slide 4 — Why We Chose This Path ("AI-Guru") *(~1 min)*

**Headline:** *"Simplifying complex workflows to prove the versatility of modern AI."*

- **The Purpose:** To demonstrate that AI can solve real-world workflow bottlenecks. Instead of forcing scientists to write complex queries to find the best material, we use AI to bridge the gap between human intent and the underlying data.
- **Showcasing Multiple Technologies:** "AI-Guru" isn't just a chatbot. It is an orchestration of **RAG**, **Semantic Embeddings**, **Mathematical Scoring & Ranking**, and **Explainable AI (XAI)** working together.
- **The Design Context:** Since the scope was intentionally open-ended, we proactively created an open-ended intelligence engine. Rather than solving one narrow problem, we demonstrated the power of AI to synthesize multiple complex capabilities at once.

---

## Slide 5 — Problem Statement & AI Vision *(~1 min)*

**Headline:** *"SQL is rigid. Scientific discovery requires semantic intent."*

- **The Problem:** The Task 1 database is incredibly powerful, but querying it requires knowing exact SQL thresholds (e.g., `band_gap > 1.0 AND energy_above_hull = 0`). 
- **The Vision:** Allow a material scientist to type: *"Find a cheap, highly stable semiconductor without lithium"* and have the system translate that into mathematical weights, semantic intent, and strict elemental filters.
- **The Goal:** Not just to *find* the material, but to use Explainable AI (XAI) to tell the scientist exactly *why* it was selected and its *potential real-world usage*.

---

## Slide 6 — Deliverables: What Was Planned *(~30 sec)*

- **Data Foundation:** Semantic Feature Engineering Pipeline (Task 1 DB → ChromaDB)
- **Retrieval:** Vector Database Integration (Local SentenceTransformers)
- **Orchestration:** LLM Integration & Intent Extraction (LangChain + OpenAI)
- **Intelligence:** Hybrid Recommendation Engine & Explainable AI Generation
- **Delivery:** Interactive User Interface & Persistent Disk Caching

> *(We revisit this on the last slide.)*

---

## Slide 7 — Architecture: Hybrid RAG System *(~1.5 min)*

**Headline:** *"Retrieval-Augmented Generation tailored for Materials Science."*

```
User Query → LLM Intent Extractor → Hybrid Search (Chroma) → Mathematical Re-Ranking → LLM Explainer → UI
```

### 1. The Vector Database
- **Model:** `all-MiniLM-L6-v2` (fast, local sentence-transformer).
- **Metadata:** Injected exact numerical values (density, cost, elements) directly into ChromaDB for hard filtering alongside the semantic vector.

### 2. The Hybrid Search Concept
- **Semantic:** Finds materials that "sound" like the user's need.
- **Deterministic Filter:** Strictly enforces `avoid_elements` (e.g., no Cobalt) at the vector level.
- **Algorithmic Re-ranking:** A custom scoring function that re-ranks the semantic results based on mathematical weights (cost vs. stability) extracted by the LLM.

---

## Slide 8 — The Semantic Payload: What Did We Embed? *(~1.5 min)*

**Headline:** *"Empowering semantic search by translating rows into human sentences."*

To perform semantic search, we didn't just embed a list of numbers. We used a Python ETL script to construct a rich, natural-language sentence for every material before embedding it into ChromaDB.

**The Semantic Template:**
> *"{formula} is a {crystal_system} material with a density of {density} g/cm³, {conductivity}, and is {stability}. It has a composite score of {score} and an element rarity index of {cost_index}."*

**Example Vectorized Payload:**
> *"LiFePO4 is a orthorhombic material with a density of 3.60 g/cm³, 3.72 eV band gap, and is thermodynamically stable. It has a composite score of 0.84 and an element rarity index of 0.051."*

**Why does this matter?**
By converting raw relational data into natural language, we empower the vector database to perform semantic matching against human queries. Because of this specific payload, AI-Guru can successfully answer:
- *"Find a lightweight cubic material"* (Matches density and crystal system)
- *"Looking for a highly stable metal"* (Matches stability string and conductivity)
- *"Suggest a cheap semiconductor"* (Matches rarity index and band gap string)

---

## Slide 9 — AI Pipeline: Intent & Explainability *(~2 min)*

**Headline:** *"Controlling the LLM with strict schemas."*

### Phase 1: Intent Extraction
The first LLM call doesn't answer the user. It translates English into a strict JSON configuration:
- **Weights (sum to 1.0):** `{conductivity: 0.2, stability: 0.5, density: 0.1, cost: 0.2}`
- **Filters:** `{is_metal: False, avoid_elements: ["Li", "Mn"]}`

### Phase 2: Explainable AI (XAI)
After the hybrid search engine finds the top 3 materials, we use the LLM to generate a justification.
- **Scientific Explanation:** Why does this material mathematically fit the request?
- **Potential Usage:** What is the practical, real-world application of this specific compound?

---

## Slide 10 — Challenges, Trade-offs & Resiliency *(~4 min)*

**Headline:** *"Every shortcut was a deliberate trade-off, not an oversight."*

### 1. Handling Unpredictable Data & AI Behaviours
| Challenge | Resilient Resolution |
|---|---|
| **Vector Search Bias:** Battery datasets are heavily skewed. Searching "semiconductor" only returned Li/Mn oxides, causing filters to wipe out all results. | **Massive Over-fetching:** Increased `top_k` retrieval pool from 150 to 3,000 before applying strict elemental filters. |
| **Unpredictable LLM Formats:** Markdown blocks and unescaped newlines broke Python's `json.loads` during Intent Extraction. | **Fail-Safe Parsing:** Enforced OpenAI `json_object` format and built a bulletproof 3-stage fallback parser. |

### 2. Deliberate Architectural Trade-offs
| Decision | Chosen For | Trade-off Accepted |
|---|---|---|
| Streamlit over FastAPI | Rapid prototyping speed | Not horizontally scalable |
| Sample of 3,000 materials | Local execution performance | Reduced retrieval coverage vs. full 154k DB |
| Local `all-MiniLM-L6-v2` model | Zero external embedding API cost | Lower semantic accuracy than hosted models |
| Persistent JSON disk cache | Bypassing LLM delays & saving API costs | Not suitable for concurrent multi-user access |

---

## Slide 11 — Live Demo (Streamlit) *(~4–5 min)*

**Live Walkthrough Steps:**
1. Show the **"Intelligent Search"** sidebar.
2. Click **"Clear AI Cache"** to prove the system is running live.
3. Select an example query: *"Find a cheap, highly stable semiconductor without lithium or manganese"*
4. Wait ~5 seconds for the live LLM generation.
5. Show the **Expandable "AI Understanding" Block** (Proving Intent Extraction).
6. Show the **Material Results** (Radar charts, properties).
7. Show the **AI Explainability & Green Destaque Box**.
8. Click the exact same query again to demonstrate the **Instantaneous Disk Cache**.

---

## Slide 12 — Final Outcomes & Deliverables *(~30 sec)*

| # | Deliverable | Status |
|---|---|---|
| 1 | Semantic Feature Engineering Pipeline | ✅ Completed (Task 1 DB → ChromaDB ETL) |
| 2 | Vector Database Integration | ✅ Completed (Local SentenceTransformers + ChromaDB) |
| 3 | LLM Integration | ✅ Completed (LangChain + OpenAI gpt-4o-mini) |
| 4 | Intent Extraction Engine | ✅ Completed (JSON Schema enforced at API level) |
| 5 | Hybrid Recommendation Engine | ✅ Completed (Semantic retrieval + property re-ranking) |
| 6 | Explainable AI (XAI) Generation | ✅ Completed (Scientific explanation + Potential Usage highlight) |
| 7 | Interactive User Interface | ✅ Completed (Streamlit + Radar charts) |
| 8 | Persistent Cache & Edge-Case Handling | ✅ Completed (Docker-mounted JSON disk cache) |

---

## Slide 13 — Q&A / Discussion *(15 min)*
*(End of presentation)*

---

# 📚 Appendix & Deep-Dive Material

---

## Appendix A — The Mathematical Re-ranking Equation

ChromaDB's semantic vector search handles *initial retrieval*. Once candidates are returned, the ranking is done entirely by a deterministic property score — the vector distance is **not** part of the final ranking equation. This is what makes it a *hybrid* system.

```python
# Step 1: Normalise each property score to 0-1 range
conductivity_score = max(0, 1.0 - abs(band_gap - 1.5) / 17.89)  # peaks at 1.5eV
stability_score    = metadata["stability_score"]                   # pre-computed
density_score      = max(0, 1.0 - (density / 26.58))
cost_score         = max(0, 1.0 - relative_cost_index)

# Step 2: Apply LLM-extracted weights (auto-normalised to sum to 1.0)
score = (
    w_cond * conductivity_score +
    w_stab * stability_score    +
    w_dens * density_score      +
    w_cost * cost_score
)
```
*The semantic vector is used only for candidate pool retrieval. Final ranking is purely property-driven, giving full scientific interpretability.*

---

## Appendix B — Intent Extraction Prompt (LLM)

This is the exact system prompt sent to `gpt-4o-mini` (configurable via `OPENAI_MODEL_NAME` env var) to translate user queries into strict JSON.

```text
You are a materials science AI assistant. Extract search parameters from the query.
Output MUST be valid JSON matching this schema:
{{
    "weights": {{"conductivity": float 0-1, "stability": float 0-1, 
               "density": float 0-1, "cost": float 0-1}},
    "filters": {{"is_metal": bool or null, "avoid_elements": [list of element symbols]}}
}}
Rules:
- Weights must sum to 1.0.
- If they ask for cheap, give high weight to cost.
- If they ask to avoid an element, put its SYMBOL in avoid_elements (e.g. Iron -> Fe).
```

---

## Appendix C — Double-Fallback JSON Parser

Because LLMs occasionally output malformed JSON (like wrapping it in markdown code blocks), we built resilient parsing logic to guarantee the orchestration pipeline never breaks.

```python
# From src/ai/llm_chain.py - Intent Extraction Fallback
def extract_intent(self, query: str) -> dict:
    prompt = self.intent_prompt.format(query=query)
    response = self.llm.invoke(prompt)
    content = response.content.strip()
    
    # 1. Clean markdown formatting if the LLM hallucinated it
    if content.startswith("```json"):
        content = content[7:-3]
    elif content.startswith("```"):
        content = content[3:-3]
        
    try:
        # 2. Attempt strict JSON parsing
        return json.loads(content)
    except Exception as e:
        print(f"Failed to parse LLM intent JSON: {e}. Using defaults.")
        # 3. Ultimate Fallback: Safe defaults so the UI never crashes
        return {
            "weights": {"conductivity": 0.25, "stability": 0.25, "density": 0.25, "cost": 0.25},
            "filters": {"is_metal": None, "avoid_elements": []}
        }
```

---

## Appendix D — Permanent Disk Caching Architecture

Streamlit's `@st.cache_data` lives in RAM and dies on Docker restarts. We built a permanent JSON cache to save OpenAI API costs completely.

```python
CACHE_FILE = "/app/data/ai_cache.json" # Mounted via Docker volume to host

def run_cached_query(workflow, q: str):
    # 1. Check permanent disk cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        if q in cache:
            return cache[q]["explanation"], cache[q]["candidates"], cache[q]["intent"]
            
    # 2. Live LLM Generation (~5 seconds)
    explanation, candidates, intent = workflow.process_query(q)
    
    # 3. Write securely to disk
    cache[q] = {"explanation": explanation, "candidates": candidates, "intent": intent}
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)
```

---

## Appendix E — Production Roadmap (To-Do)

> ⚠️ **Important Disclaimer:** *The following list is not comprehensive. A detailed migration plan can only be formulated after a proper requirements analysis of the real-world application, specific user needs, and enterprise constraints. The trade-offs accepted in this proof-of-concept were deliberate — production requirements may fundamentally change the architecture.*

While this proof-of-concept successfully demonstrates the power of AI in materials science, deploying it to a true enterprise production environment requires a paradigm shift from "Prototype" to "Enterprise-Grade."

### Exercise vs Production Architecture Mapping:

| Component | Proof-of-Concept (This Project) | Production Equivalent |
|---|---|---|
| **Vector Search & Metadata** | Local ChromaDB | Pinecone, Weaviate, or AWS OpenSearch |
| **LLM Orchestration**| Synchronous LangChain in UI | Async Celery / AWS SQS workers + Redis |
| **Web Framework** | Streamlit | React/Next.js frontend + FastAPI backend |
| **Embedding Model** | Local `all-MiniLM-L6-v2` | Hosted models (e.g., text-embedding-3-small) or fine-tuned domain-specific models |
| **Cache** | Local JSON File Cache | Redis / Memcached for distributed caching |

### Critical Production Pillars to Implement:

#### 1. AI Guardrails & Safety
- **LLM Guardrails:** Implement *NeMo Guardrails* or *LlamaGuard* to prevent prompt injection, block malicious queries, and guarantee the AI never hallucinates chemical properties.
- **Persona & Tone Enforcements:** Define a strict system prompt to enforce a professional, purely scientific persona that automatically refuses to answer non-materials-science questions.

#### 2. Security & Data Governance
- **Authentication & Authorization:** Integrate OAuth2/SSO (e.g., Auth0, Okta, Azure AD) to control access to the platform based on enterprise roles.
- **Data Governance & Provenance:** Implement row-level security and maintain strict data lineage so scientists can audit exactly which underlying dataset (or paper) generated the AI response.

#### 3. Observability, Monitoring & Alerts
- **LLM Telemetry:** Deploy *LangSmith* or *Datadog LLM Observability* to track LLM latency, token usage, API failure rates, and model drift in real-time.
- **RAG Evaluation Metrics:** Implement automated pipelines to measure retrieval accuracy (Context Precision, Recall) using frameworks like *Ragas* or *TruLens*.

#### 4. UI/UX & Continuous Feedback
- **Feedback Loops:** Add "Thumbs Up / Thumbs Down" buttons directly in the UI to capture implicit user feedback and continuously evaluate retrieval quality.
- **Asynchronous Execution:** Move the heavy LLM generation completely out of the main thread. Use WebSocket connections or Server-Sent Events (SSE) to stream responses back to the UI, preventing blocking during heavy tasks.

#### 5. Infrastructure Migration (Scaling Up)
- **Vector Search:** Migrate local ChromaDB to a managed service like **Pinecone**, **Weaviate**, or **AWS OpenSearch Serverless** for high-availability vector and metadata search.
- **Asynchronous Processing:** Move the heavy LLM generation completely out of the main thread. Use **Celery** or **AWS SQS** with asynchronous background routines to prevent UI blocking during heavy tasks.
- **Advanced Metadata Storage:** For highly complex filtering at scale, offload ChromaDB's metadata dictionary to a dedicated document store like **MongoDB** or **DynamoDB**.


