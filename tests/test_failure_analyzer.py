"""
Tests for FailureAnalyzer (Task 12)
"""
import pytest
from src.failure_analyzer import FailureAnalyzer


@pytest.fixture
def analyzer():
    return FailureAnalyzer()


# ── Helpers: build minimal result dicts ──────────────────────────────────────

def make_result(faithfulness, context_relevance, answer_relevance, answer="Some answer."):
    return {
        "query_id": "test",
        "question": "What is the NIST AI RMF?",
        "generated_answer": answer,
        "scores": {
            "faithfulness": faithfulness,
            "context_relevance": context_relevance,
            "answer_relevance": answer_relevance,
        },
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_all_high_scores_is_pass(analyzer):
    """All scores above threshold → 'pass'."""
    r = make_result(faithfulness=0.9, context_relevance=0.85, answer_relevance=0.88)
    assert analyzer.categorize(r) == "pass"


def test_hallucination_detected(analyzer):
    """Good context retrieval but low faithfulness → hallucination."""
    r = make_result(faithfulness=0.4, context_relevance=0.85, answer_relevance=0.80)
    assert analyzer.categorize(r) == "hallucination"


def test_bad_generation_detected(analyzer):
    """Good retrieval + low answer relevance → bad_generation."""
    r = make_result(faithfulness=0.80, context_relevance=0.85, answer_relevance=0.35)
    assert analyzer.categorize(r) == "bad_generation"


def test_wrong_chunk_detected(analyzer):
    """Low context relevance + low faithfulness → wrong_chunk."""
    r = make_result(faithfulness=0.40, context_relevance=0.30, answer_relevance=0.55)
    assert analyzer.categorize(r) == "wrong_chunk"


def test_missing_context_detected(analyzer):
    """Low context relevance only → missing_context."""
    r = make_result(faithfulness=0.75, context_relevance=0.30, answer_relevance=0.75)
    assert analyzer.categorize(r) == "missing_context"


def test_edge_case_deflection(analyzer):
    """LLM correctly says it cannot answer → edge_case_ok."""
    r = make_result(
        faithfulness=0.3, context_relevance=0.2, answer_relevance=0.2,
        answer="I cannot answer this question as it is not related to AI governance."
    )
    assert analyzer.categorize(r) == "edge_case_ok"


def test_analyze_report_adds_distribution(analyzer):
    """analyze_report should add failure_type to each result and distribution to summary."""
    report = {
        "summary": {"total_queries": 2, "passed": 1, "failed": 1, "hitl_flagged": 1},
        "results": [
            make_result(faithfulness=0.9, context_relevance=0.9, answer_relevance=0.9),
            make_result(faithfulness=0.3, context_relevance=0.85, answer_relevance=0.8),
        ]
    }
    enriched = analyzer.analyze_report(report)

    # Every result should now have a failure_type
    for r in enriched["results"]:
        assert "failure_type" in r

    # Summary should have failure_distribution
    assert "failure_distribution" in enriched["summary"]
    dist = enriched["summary"]["failure_distribution"]
    assert dist.get("pass", 0) == 1
    assert dist.get("hallucination", 0) == 1
