## 7. Enterprise AI Risk Patterns

| Risk | What It Is | Mitigation |
|---|---|---|
| **Model drift** | Performance degrades as real-world data shifts | Drift detection (PSI, KL divergence), scheduled retraining, champion-challenger eval, performance dashboards, alerting |
| **Hallucination** | LLM generates plausible but wrong content | RAG, grounding in verified sources, confidence scoring, source citation, fact-checking layer, output validation gates, HITL for high-stakes |
| **Bias / fairness** | Model disadvantages protected groups | Bias eval (demographic parity, equalized odds), diverse training data, fairness constraints, subgroup monitoring, model cards |
| **Data poisoning** | Adversarial manipulation of training data | Data provenance controls, validation pipelines, anomaly detection, red-teaming, supply chain verification |
| **Prompt injection** | Crafted inputs override system instructions | Input sanitization, system prompt isolation, output filtering, tool-use sandboxing, instruction hierarchy, LLM guardrails (NeMo Guardrails, Llama Guard) |
| **PII leakage** | Model outputs contain personal/sensitive info | PII detection/redaction in I/O, data minimization, access controls, differential privacy, training data scrubbing, output filters |
| **Jailbreak / adversarial** | Crafted inputs bypass safety guardrails | Red-teaming, automated adversarial testing, robustness evals, content policy filters, rate limiting |
| **Supply chain risk** | Third-party models/datasets/APIs introduce vulnerabilities | Vendor assessment, model card review, API security review, dependency scanning, SBOM for AI |

### JD Vocabulary
"eval harness," "guardrails," "model card," "champion-challenger," "drift detection," "HITL," "approval gates," "audit trail," "red-teaming," "PII redaction," "RAG grounding," "instruction hierarchy," "fairness metrics," "subgroup analysis"

---