import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import random
from src.ai.llm_chain import AIWorkflow
from src.ai.queries import PREDEFINED_QUERIES, ALL_QUERIES

# Page Config
st.set_page_config(
    page_title="Material Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .reportview-container {
        background: #fafafa;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    h1, h2, h3 {
        color: #1e3d59;
    }
    .stAlert {
        border-radius: 8px;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #ff6e40;
        color: white;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #ff5722;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1e3d59;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #757575;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# We remove cache_resource temporarily to force Streamlit to load the new JSON logic!
def load_workflow():
    return AIWorkflow()

def create_radar_chart(candidates):
    if not candidates:
        return None
        
    fig = go.Figure()
    
    categories = ['Conductivity Score', 'Stability Score', 'Density Score', 'Cost Score']
    
    for i, c in enumerate(candidates[:3]): # Max 3 for readability
        meta = c['metadata']
        
        # Calculate raw normalized scores for the radar chart
        cond = max(0, 1.0 - abs(meta.get('band_gap', 0.0) - 1.5) / 17.89)
        stab = max(0, 1.0 - (meta.get('stability_score', 0.0) / 9.71))
        dens = max(0, 1.0 - (meta.get('density', 0.0) / 26.58))
        cost = max(0, 1.0 - meta.get('relative_cost_index', 1.0))
        
        values = [cond, stab, dens, cost]
        # Close the polygon
        values.append(values[0])
        categories_closed = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_closed,
            fill='toself',
            name=c['formula']
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="Multi-Objective Comparison",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

# Permanent Disk Cache for AI Queries (Survives Docker Restarts)
CACHE_FILE = "/app/data/ai_cache.json"

def run_cached_query(workflow, q: str):
    # Try to load from disk cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
            if q in cache:
                return cache[q]["explanation"], cache[q]["candidates"], cache[q]["intent"]
        except Exception:
            pass # Ignore read errors and just run the query
            
    # Run the actual AI workflow
    explanation, candidates, intent = workflow.process_query(q)
    
    # Save to disk cache
    try:
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
        cache[q] = {
            "explanation": explanation,
            "candidates": candidates,
            "intent": intent
        }
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Failed to write cache: {e}")
        
    return explanation, candidates, intent

def main():
    st.title("🔬 Material Intelligence")
    st.markdown("Semantic exploration, recommendation, and explainable AI for materials science.")
    
    with st.spinner("Loading AI Models..."):
        workflow = load_workflow()

    # Sidebar
    with st.sidebar:
        st.header("🔍 Intelligent Search")
        
        # Session state functions to update text area and trigger search automatically
        def set_query(q):
            st.session_state.query_widget = q
            st.session_state.trigger_search = True
            
        def set_random_query():
            st.session_state.query_widget = random.choice(ALL_QUERIES)
            st.session_state.trigger_search = True
            
        query_input = st.text_area(
            "What kind of material are you looking for?",
            placeholder="Type your own query or select an example below...",
            height=100,
            key="query_widget"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            search_btn = st.button("🚀 Analyze", use_container_width=True)
        with col2:
            st.button("🎲 Random", on_click=set_random_query, use_container_width=True)
            
        if search_btn:
            st.session_state.trigger_search = True
            
        st.markdown("---")
        st.markdown("### Example Queries by Area")
        
        # Create an expander for each category
        for category, queries in PREDEFINED_QUERIES.items():
            with st.expander(category):
                # Show first 3 of each category to avoid overwhelming the UI
                for idx, q in enumerate(queries[:3]):
                    st.button(f"📝 {q}", on_click=set_query, args=(q,), key=f"btn_{category}_{idx}")

        st.markdown("---")
        if st.button("🧹 Clear AI Cache", use_container_width=True, help="Wipes the permanent disk cache so you can demonstrate the live AI generation delay"):
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "w") as f:
                    json.dump({}, f)
            st.toast("Disk cache cleared successfully!", icon="🧹")

    # Main Content Execution
    if getattr(st.session_state, 'trigger_search', False) and st.session_state.get('query_widget'):
        query = st.session_state.query_widget
        st.session_state.trigger_search = False # Reset flag so it doesn't loop
        
        with st.spinner("🧠 AI is analyzing your intent and retrieving materials..."):
            try:
                explanation, candidates, intent = run_cached_query(workflow, query)
                st.session_state.results = {
                    "query": query,
                    "explanation": explanation,
                    "candidates": candidates,
                    "intent": intent
                }
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)
                st.session_state.results = None

    # Main Content Rendering
    if st.session_state.get('results'):
        res = st.session_state.results
        query = res["query"]
        explanation = res["explanation"]
        candidates = res["candidates"]
        intent = res["intent"]
        
        if not candidates:
            st.error("No materials matched your exact query constraints.")
            return
            
        # Intent Tracking
        with st.expander("🔍 How AI understood your query", expanded=True):
            st.markdown(f"**Your Query:** _{query}_")
            
            w = intent.get('weights', {})
            f = intent.get('filters', {})
            
            st.markdown(f"""
            **Optimizing For:**
            - Conductivity: `{w.get('conductivity', 0.0):.2f}`
            - Stability: `{w.get('stability', 0.0):.2f}`
            - Density: `{w.get('density', 0.0):.2f}`
            - Cost: `{w.get('cost', 0.0):.2f}`
            
            **Constraints:**
            - Is Metal: `{f.get('is_metal')}`
            - Avoid Elements: `{', '.join(f.get('avoid_elements', [])) if f.get('avoid_elements') else 'None'}`
            """)
        
        # Top Matches Panel
        st.header("🏆 Top Recommendations")
        
        tabs = st.tabs([f"#{i+1}: {c['formula']}" for i, c in enumerate(candidates[:3])])
        
        for i, tab in enumerate(tabs):
            with tab:
                match = candidates[i]
                meta = match['metadata']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{match['scientific_score']:.2f}</div>
                        <div class="metric-label">Composite Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{meta.get('density', 0.0):.2f}</div>
                        <div class="metric-label">Density (g/cm³)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{meta.get('band_gap', 0.0):.2f}</div>
                        <div class="metric-label">Band Gap (eV)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{meta.get('stability_score', 0.0):.3f}</div>
                        <div class="metric-label">Energy Above Hull</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if "explanation" in match:
                    expl_text = match["explanation"]
                    try:
                        expl_text_clean = expl_text.strip()
                        if expl_text_clean.startswith("```json"):
                            expl_text_clean = expl_text_clean.replace("```json", "").replace("```", "").strip()
                        elif expl_text_clean.startswith("```"):
                            expl_text_clean = expl_text_clean.replace("```", "").strip()
                            
                        parsed = json.loads(expl_text_clean, strict=False)
                        st.info("### AI Explainability\n\n" + parsed.get("scientific_explanation", ""))
                        st.success("### 💡 Destaque: Potential Usage\n\n" + parsed.get("potential_usage", ""))
                    except Exception:
                        # Fallback: if it's not JSON, try to parse it as the old Markdown format
                        split_str = None
                        if "**Potential Usage:**" in expl_text:
                            split_str = "**Potential Usage:**"
                        elif "💡 **Potential Usage:**" in expl_text:
                            split_str = "💡 **Potential Usage:**"
                        elif "Potential Usage:" in expl_text:
                            split_str = "Potential Usage:"
                            
                        if split_str:
                            parts = expl_text.split(split_str, 1)
                            main_expl = parts[0].strip().rstrip('-').strip()
                            usage = parts[1].strip()
                            st.info("### AI Explainability\n\n" + main_expl)
                            st.success("### 💡 Destaque: Potential Usage\n\n" + usage)
                        else:
                            # Absolute final fallback for malformed text
                            st.info("### AI Explainability\n\n" + expl_text)
        
        st.markdown("---")
        
        # Comparison View
        st.header("📊 Material Comparison")
        
        col_chart, col_table = st.columns([1, 1.2])
        
        with col_chart:
            fig = create_radar_chart(candidates)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col_table:
            table_data = []
            for c in candidates[:5]:
                m = c['metadata']
                table_data.append({
                    "Formula": c['formula'],
                    "Score": f"{c['scientific_score']:.2f}",
                    "Crystal": m.get('crystal_system', 'N/A'),
                    "Density": f"{m.get('density', 0.0):.2f}",
                    "Band Gap": f"{m.get('band_gap', 0.0):.2f}",
                    "Hull Energy": f"{m.get('stability_score', 0.0):.3f}",
                    "Rarity Index": f"{m.get('relative_cost_index', 0.0):.3f}"
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
