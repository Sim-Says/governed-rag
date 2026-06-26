"""
Regression Suite (Task 11)
==========================
Purpose: Ensure that any change to the pipeline (chunk size, model, prompt)
         does NOT degrade our evaluation scores below the saved baseline.

How it works:
  1. Load the baseline scores from data/baselines/baseline_v1.json
  2. Run a LIVE mini-evaluation on a small sample of golden pairs
  3. Assert the live scores are within an acceptable tolerance of the baseline

Run with:
  $env:PYTHONPATH="."; .venv\Scripts\python.exe -m pytest tests\test_regression.py -v
"""
import json
import pytest
from pathlib import Path

BASELINE_PATH = Path("data/baselines/baseline_v1.json")
TOLERANCE     = 0.05   # allow up to 5% drop from baseline before failing


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_baseline() -> dict:
    """Load the saved baseline report."""
    if not BASELINE_PATH.exists():
        pytest.skip("No baseline found yet. Run `python -m src.run_eval` first, then copy the result to data/baselines/baseline_v1.json")
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_baseline_score(baseline: dict, metric: str) -> float:
    """Pull a mean score out of the baseline summary."""
    key = f"{metric}_mean"
    return baseline["summary"]["scores_summary"][key]


def get_baseline_hitl_rate(baseline: dict) -> float:
    total = baseline["summary"]["total_queries"]
    flagged = baseline["summary"]["hitl_flagged"]
    return flagged / total if total else 0.0


def get_live_scores() -> dict:
    """
    Run a lightweight live evaluation on the first 5 golden pairs.
    Returns a dict of mean scores: faithfulness, answer_relevance, context_relevance.
    """
    from src.chunker import chunk_file
    from src.vector_store import VectorStore
    from src.rag_pipeline import RAGPipeline
    from src.evaluator import RAGEvaluator

    # Load and index corpus
    all_chunks = []
    for fp in sorted(Path("data/docs").glob("*.md")):
        all_chunks.extend(chunk_file(str(fp)))

    store = VectorStore(persist_path="data/chroma_db")
    store.clear()
    store.add_chunks(all_chunks)

    pipeline  = RAGPipeline(store)
    evaluator = RAGEvaluator()

    with open("data/golden/golden_qa.json", encoding="utf-8") as f:
        golden = json.load(f)

    # Only sample the first 5 pairs to keep the regression run fast (~3 min)
    sample = golden[:5]
    score_rows = []
    for pair in sample:
        rag_result = pipeline.ask(pair["question"])
        scores     = evaluator.evaluate(rag_result, pair)
        score_rows.append(scores)

    def mean(key):
        return sum(r[key] for r in score_rows) / len(score_rows)

    return {
        "faithfulness":      mean("faithfulness"),
        "answer_relevance":  mean("answer_relevance"),
        "context_relevance": mean("context_relevance"),
        "hitl_rate": sum(
            1 for r in score_rows if r["faithfulness"] < 0.7
        ) / len(score_rows),
    }


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def baseline():
    return load_baseline()


@pytest.fixture(scope="module")
def live():
    """Run the live mini-eval once and share results across all tests."""
    return get_live_scores()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_faithfulness_no_regression(baseline, live):
    """
    Faithfulness must not drop more than TOLERANCE below baseline.
    A drop here means the LLM has started hallucinating more than before.
    """
    baseline_score = get_baseline_score(baseline, "faithfulness")
    floor          = baseline_score - TOLERANCE
    assert live["faithfulness"] >= floor, (
        f"Faithfulness REGRESSION: live={live['faithfulness']:.3f} "
        f"< baseline={baseline_score:.3f} - tolerance={TOLERANCE}"
    )


def test_answer_relevance_no_regression(baseline, live):
    """
    Answer relevance must not drop more than TOLERANCE below baseline.
    A drop here means answers are drifting off-topic.
    """
    baseline_score = get_baseline_score(baseline, "answer_relevance")
    floor          = baseline_score - TOLERANCE
    assert live["answer_relevance"] >= floor, (
        f"Answer Relevance REGRESSION: live={live['answer_relevance']:.3f} "
        f"< baseline={baseline_score:.3f} - tolerance={TOLERANCE}"
    )


def test_context_relevance_no_regression(baseline, live):
    """
    Context relevance must not drop more than TOLERANCE below baseline.
    A drop here usually means the chunk size or vector store changed.
    """
    baseline_score = get_baseline_score(baseline, "context_relevance")
    floor          = baseline_score - TOLERANCE
    assert live["context_relevance"] >= floor, (
        f"Context Relevance REGRESSION: live={live['context_relevance']:.3f} "
        f"< baseline={baseline_score:.3f} - tolerance={TOLERANCE}"
    )


def test_hitl_rate_not_spiking(baseline, live):
    """
    The % of answers flagged for human review must not spike > 10% above baseline.
    A spike means our model or retrieval has degraded significantly.
    """
    baseline_rate = get_baseline_hitl_rate(baseline)
    ceiling       = baseline_rate + 0.10
    assert live["hitl_rate"] <= ceiling, (
        f"HITL Rate SPIKE: live={live['hitl_rate']:.2%} "
        f"> baseline={baseline_rate:.2%} + 10%"
    )
