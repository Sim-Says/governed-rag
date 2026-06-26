# Architecture — Governed RAG

This document describes the full technical architecture of the Governed RAG system: how components are structured, how data flows through the pipeline, and how the governance layer enforces auditability.

---

## 1. High-Level System Overview

```mermaid
graph TD
    subgraph Ingestion
        A[Markdown Corpus] --> B[Chunker]
        B --> C[Embedder - all-MiniLM-L6-v2]
        C --> D[(ChromaDB Vector Store)]
    end

    subgraph Query
        E[User Question] --> F[Query Embedder]
        F --> G{Similarity Search}
        D --> G
        G --> H[Top-5 Chunks Retrieved]
    end

    subgraph Generation
        H --> I[RAG Pipeline]
        E --> I
        I --> J[gemma3:4b via Ollama Cloud]
        J --> K[Generated Answer]
    end

    subgraph Governance
        K --> L[Ragas Evaluator]
        H --> L
        E --> L
        L --> M{Score >= Threshold?}
        M -->|Yes| N[Serve Answer to User]
        M -->|No| O[HITL Queue]
        O --> P[Human Review & Correction]
    end
```

---

## 2. Evaluation Pipeline

Every answer flows through the Ragas triad before being served or flagged.

```mermaid
graph TD
    A[RAG Result] --> B[Ragas Evaluate]
    GD[Golden Reference Answer] --> B

    B --> C[Faithfulness Score]
    B --> D[Answer Relevancy Score]
    B --> E[Context Precision Score]

    C --> F{Threshold Check}
    D --> F
    E --> F

    F -->|All pass| G[EvalReporter - PASS]
    F -->|Any fail| H[EvalReporter - FAIL]
    F -->|Faithfulness < 0.7| I[HITLCheckpoint - Queue]

    H --> J[FailureAnalyzer]
    J --> K{Root Cause?}
    K --> L[hallucination]
    K --> M[missing_context]
    K --> N[wrong_chunk]
    K --> O[bad_generation]
    K --> P[edge_case_ok]
```

---

## 3. Regression Testing Flow

This is how we prevent silent performance degradation every time the pipeline changes.

```mermaid
graph TD
    A[First Full Eval Run] -->|Save report| B[(baseline_v1.json)]

    C[Code Change e.g. new chunk size] --> D[Run Mini Eval - 5 questions]
    D --> E[Live Scores]
    B --> F{Compare}
    E --> F

    F -->|Score >= Baseline minus 5 percent| G[PASS - Change accepted]
    F -->|Score < Baseline minus 5 percent| H[FAIL - Regression detected]

    H --> I[Investigate with FailureAnalyzer]
    I --> J[Fix and re-run]
```

---

## 4. HITL Workflow

```mermaid
graph TD
    A[Scored Answer] --> B{Faithfulness >= 0.7?}
    B -->|Yes| C[Serve to User]
    B -->|No| D[HITLCheckpoint.flag_for_review]
    D --> E[(data/hitl_queue/*.json)]
    E --> F[Human Expert Opens File]
    F --> G{Agree with AI?}
    G -->|Yes, approve| H[resolve_review - approved]
    G -->|No, correct| I[resolve_review - corrected answer]
    H --> J[(Audit Log)]
    I --> J
    I --> K[Update Corpus if gap found]
```

---

## 5. Component Dependency Map

```mermaid
graph TD
    chunker --> vector_store
    vector_store --> rag_pipeline
    rag_pipeline --> evaluator
    evaluator --> hitl
    evaluator --> reporter
    evaluator --> failure_analyzer
    reporter --> run_eval
    rag_pipeline --> run_eval
    hitl --> run_eval
    failure_analyzer --> run_eval
    reporter --> test_regression
    evaluator --> test_regression
```

---

## 6. Data Flow — Ingestion vs. Query

| Stage | Input | Process | Output |
|---|---|---|---|
| **Ingestion** | `.md` files in `data/docs/` | Chunk → Embed | Vectors in ChromaDB |
| **Query** | User natural language question | Embed → Similarity Search | Top-5 most relevant chunks |
| **Generation** | User question + retrieved chunks | Prompt → LLM call | Natural language answer |
| **Evaluation** | Answer + chunks + reference | Ragas metrics | Scores 0.0–1.0 per metric |
| **Governance** | Scores | Threshold gate | Serve or queue for HITL |
| **Regression** | Live scores vs. baseline | Statistical comparison | Pass or regression alert |

---

## 7. Key Design Decisions

| Decision | Chosen Approach | Trade-off |
|---|---|---|
| **Embedding model** | Local `all-MiniLM-L6-v2` via PyTorch | No API cost or network dependency; less powerful than commercial models |
| **Vector store** | ChromaDB (local SQLite) | Zero infrastructure setup; not horizontally scalable |
| **Generation model** | `gemma3:4b` via Ollama Cloud | Compact and fast; larger models would improve answer quality |
| **Judge model** | `ministral-3:8b` via Ollama Cloud | Available on current cloud instance; GPT-4 class would grade more accurately |
| **HITL storage** | JSON files in `data/hitl_queue/` | Fully transparent and debuggable; not integrated with enterprise ticketing |
| **Eval framework** | Ragas with LangChain wrappers | Best-in-class RAG metrics; required careful bridging due to version changes |
