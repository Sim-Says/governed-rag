## 8. HITL Workflow Patterns

| Pattern | How It Works | When to Use |
|---|---|---|
| **Review-then-approve** | AI generates → human reviews → approves/rejects/edits → delivered | High-stakes (contracts, compliance, customer comms, financial decisions). Default for governed enterprise workflows. |
| **Escalate-on-confidence-threshold** | AI outputs confidence score → above threshold auto-approves → below routes to human review | High-volume classification/extraction. **Most common pattern in enterprise AI workflow products.** |
| **Human veto (human-in-command)** | AI operates autonomously, human retains right to veto/override any decision | Required by EU AI Act for high-risk systems. Autonomous agents, automated decisioning. |
| **Sample-based audit** | AI operates autonomously → random sample (5-10%) routed to human review | Low-risk, high-volume (tagging, routing, summarization). Quality monitoring without bottleneck. |
| **Escalation on red-flag** | Guardrail checks → red-flag detected (PII, toxicity, policy) → escalate to human | Safety/content moderation, compliance-sensitive outputs. |
| **Supervisor override / multi-approver** | AI → first reviewer → if uncertain, escalate to supervisor → multi-approval for highest stakes | Hierarchical approval in regulated environments (financial, legal, healthcare). |
