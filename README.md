# Governed RAG

> **A RAG pipeline that refuses to answer unless it can mathematically prove it is right.**

🔴 **Live Dashboard:** [https://governed-rag.streamlit.app/](https://governed-rag.streamlit.app/)

---

## 📄 Case Study
See [docs/case-study.md](./docs/case-study.md) for the full product case study covering problem framing, architecture decisions, eval framework design, and baseline results.

---


## What This Is

Enterprise AI systems that answer questions from internal policy documents have a critical problem: **hallucinations are unacceptable**. A finance analyst asking about RBI guidelines, or a compliance officer querying the EU AI Act, cannot risk receiving a confidently-wrong AI-generated answer.

**Governed RAG** addresses this with a full, measurable governance layer *around* the standard RAG pattern:

- Every answer is **automatically scored** for faithfulness, relevance, and context quality using a Judge LLM
- Answers that fall below confidence thresholds are **intercepted before reaching the user** and placed in a human review queue
- Every pipeline change is **regression-tested** against a saved baseline to detect score drift before it reaches production
- Every failure is **categorized** to its root cause — hallucination, retrieval gap, or generation error — so engineers know exactly what to fix

---

## Architecture

```
Corpus (Markdown Docs)
        │
        ▼
  [ Chunker ]  →  500-char semantic chunks with overlap
        │
        ▼
  [ Embedder ]  →  all-MiniLM-L6-v2 via PyTorch (local, no API)
        │
        ▼
  [ ChromaDB ]  →  Persisted local vector store
        │
     (retrieval)
        │
  [ User Query ] → embedded → top-5 similar chunks retrieved
        │
        ▼
  [ RAG Pipeline ]  →  gemma3:4b via Ollama Cloud generates answer
        │
        ▼
  [ Ragas Evaluator ]  →  ministral-3:8b judges:
    - Faithfulness       (hallucination check)
    - Answer Relevancy   (on-topic check)
    - Context Precision  (retrieval quality check)
        │
        ├──[score >= threshold]──→  Serve answer
        │
        └──[score < threshold]──→  [ HITL Queue ]
                                         │
                                   Human expert reviews,
                                   corrects, and logs
```

---

## Project Structure

```
governed-rag/
│
├── data/
│   ├── docs/               # Markdown policy corpus (NIST, EU AI Act, DPDP, etc.)
│   ├── golden/             # 50+ curated Q&A pairs for evaluation
│   ├── baselines/          # Saved baseline eval reports for regression testing
│   ├── results/            # Output JSON reports from evaluation runs
│   └── hitl_queue/         # Low-confidence answers pending human review
│
├── src/
│   ├── dashboard.py        # Streamlit UI for visualizing evaluation metrics
│   ├── chunker.py          # Splits Markdown files into semantic chunks
│   ├── embedder.py         # Converts chunks to vectors (all-MiniLM-L6-v2)
│   ├── vector_store.py     # ChromaDB wrapper for similarity search
│   ├── rag_pipeline.py     # End-to-end RAG: retrieve + generate
│   ├── evaluator.py        # Ragas-based scoring (faithfulness, relevance)
│   ├── hitl.py             # HITL checkpoint — flags low-confidence answers
│   ├── failure_analyzer.py # Root-cause categorization of evaluation failures
│   ├── reporter.py         # Generates JSON + console eval reports
│   └── run_eval.py         # Full evaluation runner across all golden pairs
│
├── tests/
│   ├── test_chunker.py
│   ├── test_vector_store.py
│   ├── test_rag_pipeline.py
│   ├── test_evaluator.py
│   ├── test_hitl.py
│   ├── test_failure_analyzer.py
│   └── test_regression.py  # Regression suite — compares live scores to baseline
│
└── docs/
    ├── architecture.md         # Full system architecture with diagrams
    └── case-study.md           # Product case study and narrative
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- An Ollama Cloud account with `gemma3:4b` and `ministral-3:8b` available
- Git

### 2. Setup

```powershell
# Clone the repo
git clone <your-repo-url>
cd governed-rag

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

Create a `.env` file at the project root:

```
OLLAMA_API_KEY=your_ollama_cloud_key
OLLAMA_BASE_URL=https://ollama.com/v1
GENERATION_MODEL=gemma3:4b
JUDGE_MODEL=ministral-3:8b
```

### 4. Add Documents

Drop your Markdown policy documents into `data/docs/`.

### 5. Run the Full Evaluation

```powershell
$env:PYTHONPATH="."; .venv\Scripts\python.exe -m src.run_eval
```

This will:
- Chunk and embed all documents
- Answer every question in the golden dataset
- Score each answer with the Judge LLM
- Save a timestamped report to `data/results/`
- Flag low-confidence answers to `data/hitl_queue/`

### 6. Save as Baseline (First Run)

```powershell
Copy-Item data/results/eval_*.json data/baselines/baseline_v1.json
```

### 7. Run Regression Suite (After Any Change)

```powershell
$env:PYTHONPATH="."; .venv\Scripts\python.exe -m pytest tests\test_regression.py -v
```

### 8. Run All Unit Tests

```powershell
.venv\Scripts\python.exe -m pytest tests\ -v --ignore=tests\test_regression.py --ignore=tests\test_evaluator.py
```

### 9. View the Dashboard

```powershell
.venv\Scripts\python.exe -m streamlit run src/dashboard.py
```

---

## Governance Model

| Layer | Mechanism | Purpose |
|---|---|---|
| **Scoring** | Ragas Triad (faithfulness, answer relevance, context precision) | Measure answer quality objectively |
| **Thresholding** | Configurable pass/fail gates per metric | Reject answers that don't meet the bar |
| **HITL Queue** | JSON-persisted review queue | Intercept and audit low-confidence answers |
| **Failure Analysis** | Root-cause categorization | Know *why* the system failed, not just that it did |
| **Regression Testing** | Baseline comparison with tolerance bands | Prevent silent performance degradation over time |

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Language | Python 3.11 | Ecosystem maturity for ML tooling |
| Vector Store | ChromaDB | Fast local setup; production-migratable to cloud |
| Embeddings | `all-MiniLM-L6-v2` via Sentence-Transformers | Runs fully local, no API calls required |
| ML Framework | PyTorch | Powers the embedding model computation |
| Generation LLM | `gemma3:4b` via Ollama Cloud | Grounded answer generation |
| Judge LLM | `ministral-3:8b` via Ollama Cloud | Autonomous evaluation scoring |
| Evaluation | Ragas | RAG-specific metric framework |
| Testing | pytest | Industry-standard test runner |


