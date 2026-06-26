"""
Failure Analyzer (Task 12)
===========================
Purpose: When a RAG evaluation result FAILS, categorize the root cause
         so engineers know exactly what to fix.

Failure Taxonomy:
  hallucination   – LLM invented info not present in the retrieved chunks
                    Signal: low faithfulness, but high answer relevance
  missing_context – The right chunk was never retrieved from ChromaDB
                    Signal: low context relevance, but the answer "tried"
  wrong_chunk     – Irrelevant chunks were retrieved
                    Signal: low context relevance + low faithfulness
  bad_generation  – Good chunks were retrieved, but the LLM answered badly
                    Signal: high context relevance, low answer relevance
  edge_case_ok    – The question was out-of-domain; correctly deflected
                    Signal: low scores, but the question was an edge case
  pass            – Nothing to categorize; all scores above threshold
"""

from __future__ import annotations

# ── Thresholds ────────────────────────────────────────────────────────────────
FAITHFULNESS_THRESHOLD       = 0.7
CONTEXT_RELEVANCE_THRESHOLD  = 0.7
ANSWER_RELEVANCE_THRESHOLD   = 0.7


class FailureAnalyzer:
    """
    Analyzes a scored eval result and assigns a failure category.
    """

    EDGE_CASE_MARKERS = [
        "out of domain", "i don't know", "cannot answer",
        "i am not able", "not relevant", "i cannot"
    ]

    def categorize(self, result: dict) -> str:
        """
        Given a result dict with 'scores' and 'generated_answer',
        return one of:
          'pass' | 'hallucination' | 'missing_context' |
          'wrong_chunk' | 'bad_generation' | 'edge_case_ok'
        """
        scores           = result["scores"]
        faithfulness     = scores["faithfulness"]
        context_rel      = scores.get("context_relevance",  scores.get("context_precision", 0.0))
        answer_rel       = scores.get("answer_relevance",   scores.get("answer_relevancy",  0.0))
        generated_answer = result.get("generated_answer", "").lower()

        # ── All good ─────────────────────────────────────────────────────────
        if (faithfulness     >= FAITHFULNESS_THRESHOLD and
            context_rel      >= CONTEXT_RELEVANCE_THRESHOLD and
            answer_rel       >= ANSWER_RELEVANCE_THRESHOLD):
            return "pass"

        # ── Edge case correctly deflected ─────────────────────────────────────
        if any(marker in generated_answer for marker in self.EDGE_CASE_MARKERS):
            return "edge_case_ok"

        # ── Hallucination: LLM made things up ─────────────────────────────────
        # Good retrieval (context was relevant) but LLM went off-script
        if faithfulness < FAITHFULNESS_THRESHOLD and context_rel >= CONTEXT_RELEVANCE_THRESHOLD:
            return "hallucination"

        # ── Bad generation: Chunks were fine, LLM answer was irrelevant ───────
        if context_rel >= CONTEXT_RELEVANCE_THRESHOLD and answer_rel < ANSWER_RELEVANCE_THRESHOLD:
            return "bad_generation"

        # ── Wrong chunk: Retrieval pulled in irrelevant documents ─────────────
        # Faithfulness is also low because the chunks were wrong to begin with
        if context_rel < CONTEXT_RELEVANCE_THRESHOLD and faithfulness < FAITHFULNESS_THRESHOLD:
            return "wrong_chunk"

        # ── Missing context: Retrieval found nothing useful ───────────────────
        if context_rel < CONTEXT_RELEVANCE_THRESHOLD:
            return "missing_context"

        # ── Fallback ──────────────────────────────────────────────────────────
        return "unknown"

    def analyze_report(self, report: dict) -> dict:
        """
        Run categorization on every result in a full eval report.
        Returns an augmented report with 'failure_type' on each result
        and a summary breakdown of failure types.
        """
        results = report.get("results", [])
        counts: dict[str, int] = {}

        for r in results:
            category     = self.categorize(r)
            r["failure_type"] = category
            counts[category] = counts.get(category, 0) + 1

        report["summary"]["failure_distribution"] = counts
        return report

    @staticmethod
    def print_failure_distribution(report: dict):
        """Pretty-print the failure type breakdown."""
        dist  = report["summary"].get("failure_distribution", {})
        total = report["summary"]["total_queries"]

        print(f"\n{'='*50}")
        print("  FAILURE CATEGORY BREAKDOWN")
        print(f"{'='*50}")
        for category, count in sorted(dist.items()):
            pct = count / total * 100 if total else 0
            bar = "#" * count
            print(f"  {category:<20} {count:>3}  ({pct:4.1f}%)  {bar}")
        print(f"{'='*50}\n")
