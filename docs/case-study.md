# Case Study: Building "Governed RAG" for Regulated Enterprises

**"A RAG pipeline that refuses to answer unless it can prove it's right."**

**Role:** AI Product Manager & Architect  
**Timeline:** Overnight sprint to MVP, 5 days to eval-gated production  
**Tech Stack:** Python, ChromaDB, Sentence-Transformers, Ragas (LLM-as-a-Judge), LangChain, Ollama, Pytest  
**Live Dashboard:** [https://governed-rag.streamlit.app/](https://governed-rag.streamlit.app/)

---

## 🛑 The Problem: The Unacceptable Risk of "Blind" RAG

Enterprises in highly regulated sectors (finance, healthcare) cannot afford AI hallucinations. A standard Retrieval-Augmented Generation (RAG) system blindly retrieves context and generates answers. If the retrieved context is wrong, or the LLM misinterprets a policy, the system confidently provides incorrect guidance on critical compliance frameworks like the EU AI Act, NIST AI RMF, or the DPDP Act.

**The challenge:** Building a RAG system that structurally guarantees it will only serve an answer if it is mathematically confident the output is faithful to the source material.

---

## 💡 The Solution: A Governance-First RAG Architecture

I designed and implemented **Governed RAG** — a RAG pipeline heavily wrapped in quantitative evaluation and automated safety gates.

### 1. The Core Pipeline
* **Local Knowledge Base:** I ingested Markdown documents containing complex regulatory frameworks (NIST, ISO, EU AI Act, RBI guidelines).
* **Deterministic Chunking & Local Embeddings:** I built a chunker using a 500-character / 50-character overlap window. I embedded this locally using `all-MiniLM-L6-v2` via `sentence-transformers` and indexed it in ChromaDB for strict local execution, without exposing data to external embedding APIs.
* **Constrained Generation:** I leveraged a strict system prompt instructing the model to answer *only* from the retrieved context, citing its sources.

### 2. The Evaluation Harness (Ragas)
Standard RAG relies on qualitative "vibes." I implemented quantitative evaluation using **Ragas (LLM-as-a-Judge)**. 
* **Product Decision — Why Ragas?** I evaluated custom prompt-based scoring, TruLens, and Ragas. I chose Ragas because its strict separation of the "RAG Triad" (Faithfulness, Answer Relevance, Context Precision) allowed me to isolate whether a failure was a search problem (bad retrieval) or a generation problem (hallucination).

### 3. Automated Human-in-the-Loop (HITL)
If an answer scores below a threshold, it is never shown to the user. Instead, an automated `HITLCheckpoint` intercepts the response and writes a timestamped audit artifact into a pending review queue.
* **Product Decision — Why a 0.70 Faithfulness Threshold?** Setting this too high (0.90+) floods the HITL queue with false positives, overwhelming human reviewers. Setting it too low (<0.50) risks serving non-compliant answers to users. 0.70 represents the optimal business boundary between operational efficiency and regulatory safety.
* **Operational Model:** The HITL queue is designed to be owned by a Tier 2 Compliance Operations team. The JSON file artifacts act as a permanent, legally discoverable audit trail of AI intervention.

---

## 📊 Results & Real-World Validation (Baseline v1)

To validate the system, I built a 50-question "Golden Dataset" categorized into regulatory questions, framework comparisons, enterprise policies, and adversarial edge cases. I built a CLI test runner and a 5-category `FailureAnalyzer` to interpret the results.

**Baseline v1 Results:**
* **Total Queries Evaluated:** 50
* **Pass Rate:** 22% (11/50)
* **HITL Interception Rate:** 60% (30/50)

**Why these results are a success:** 
While a 22% pass rate highlights gaps in my initial document corpus, the **60% HITL interception rate proves the safety mechanism works.** The system successfully identified 30 answers that were unfaithful or lacked context, safely queuing them for human review rather than exposing the enterprise to compliance risk.

---

## 🛠️ Key Product & Governance Challenges Surmounted

* **Disambiguating Refusals from Hallucinations:** Out of the box, evaluation metrics penalize an LLM for safely refusing to answer an out-of-domain question (e.g., "I cannot answer that"). I designed a custom programmatic `FailureAnalyzer` to identify `edge_case_ok` behaviors and separate them from true, dangerous hallucinations so my KPIs reflected reality.
* **Designing the Audit Trail:** A database felt like overkill for an MVP, but I needed extreme transparency. I designed the HITL queue to output heavily structured, timestamped JSON files. This means an external auditor doesn't need to query a database—they can simply open a folder and read the exact lifecycle of any blocked generation.
* **CI/CD Drift Prevention:** Full 50-question evaluations take ~15 minutes and block developer velocity. I architected a Regression Suite that executes a fast, 5-question mini-eval against the saved Baseline JSON, enforcing a 5% statistical tolerance band to prevent configuration drift during active development.

---

## ⏭️ Next Steps
Next Steps: Corpus enrichment to drive Pass Rate from 22% to an 85%+ SLA, then expand the golden dataset with real enterprise policy documents to test retrieval accuracy at scale.
