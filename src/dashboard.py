import streamlit as st
import json
import pandas as pd
from pathlib import Path

# Add src to Python path so we can import FailureAnalyzer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.failure_analyzer import FailureAnalyzer

st.set_page_config(page_title="Governed RAG Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Governed RAG: Evaluation Dashboard")
st.markdown("Visualizing evaluation results and Human-in-the-Loop (HITL) safety gates.")

@st.cache_data
def load_baseline():
    baseline_path = Path("data/baselines/baseline_v1.json")
    if not baseline_path.exists():
        return None
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_baseline()

if not data:
    st.error("Baseline file not found at `data/baselines/baseline_v1.json`. Please run the evaluation first.")
    st.stop()

# --- KPI METRICS ---
st.header("Overall Performance")
summary = data.get("summary", {})
total = summary.get("total_queries", 0)
passed = summary.get("passed", 0)
hitl = summary.get("hitl_flagged", 0)

pass_rate = (passed / total * 100) if total > 0 else 0
hitl_rate = (hitl / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Queries", total)
col2.metric("Pass Rate", f"{pass_rate:.1f}%")
col3.metric("HITL Flag Rate (Safety Gate)", f"{hitl_rate:.1f}%", help="Answers intercepted before reaching the user.")

st.divider()

# --- FAILURE ANALYSIS ---
st.header("Failure Distribution")
st.markdown("Categorizing the failed queries into actionable patterns.")

analyzer = FailureAnalyzer()
results = data.get("results", [])

categories = {"pass": 0, "hallucination": 0, "missing_context": 0, "wrong_chunk": 0, "bad_generation": 0, "edge_case_ok": 0, "unknown": 0}

table_data = []

for r in results:
    cat = analyzer.categorize(r)
    categories[cat] += 1
    
    # Format scores for the table
    s = r.get("scores", {})
    table_data.append({
        "Query ID": r.get("query_id"),
        "Question": r.get("question"),
        "Category": cat.upper(),
        "HITL Flag": r.get("hitl_flag", False),
        "Faithfulness": round(s.get("faithfulness", 0) or 0, 2),
        "Context Relevance": round(s.get("context_relevance", 0) or 0, 2),
        "Answer Relevance": round(s.get("answer_relevance", 0) or 0, 2)
    })

# Remove 'pass' and 'unknown' from the chart to focus purely on failures
chart_data = {k: v for k, v in categories.items() if k not in ["pass", "unknown"] and v > 0}

if chart_data:
    df_chart = pd.DataFrame(list(chart_data.items()), columns=["Failure Category", "Count"])
    st.bar_chart(df_chart.set_index("Failure Category"))
else:
    st.success("No failures to categorize!")

st.divider()

# --- DATA EXPLORER ---
st.header("Query Explorer")
st.markdown("Inspect individual query scores and categorization.")

df_table = pd.DataFrame(table_data)

# Filtering
filter_cat = st.selectbox("Filter by Category", ["All"] + list(categories.keys()))
if filter_cat != "All":
    df_table = df_table[df_table["Category"] == filter_cat.upper()]

st.dataframe(df_table, use_container_width=True, hide_index=True)
