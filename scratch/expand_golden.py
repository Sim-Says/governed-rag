import json
from pathlib import Path

# Existing golden QA data is loaded and extended
golden_file = Path("data/golden/golden_qa.json")

with open(golden_file, "r", encoding="utf-8") as f:
    existing_data = json.load(f)

# The new pairs
new_pairs = [
    # 1. 8 more regulatory questions
    {"id": "reg_003", "category": "regulatory", "question": "What are the risk categories defined by the EU AI Act?", "reference_answer": "The EU AI Act classifies AI systems into four risk categories: Unacceptable risk, High risk, Limited risk, and Minimal or no risk."},
    {"id": "reg_004", "category": "regulatory", "question": "Under the EU AI Act, what is considered an unacceptable risk?", "reference_answer": "Unacceptable risks include AI systems that manipulate human behavior to circumvent free will, systems that allow social scoring by governments, and real-time remote biometric identification in public spaces by law enforcement (with some exceptions)."},
    {"id": "reg_005", "category": "regulatory", "question": "What does the DPDP Act stand for?", "reference_answer": "The DPDP Act stands for the Digital Personal Data Protection Act of India."},
    {"id": "reg_006", "category": "regulatory", "question": "What is the primary role of a Data Fiduciary under the DPDP Act?", "reference_answer": "A Data Fiduciary determines the purpose and means of processing personal data and is responsible for protecting it and ensuring compliance with the DPDP Act."},
    {"id": "reg_007", "category": "regulatory", "question": "Does the RBI outline guidelines for algorithmic trading?", "reference_answer": "Yes, the Reserve Bank of India (RBI) and SEBI provide strict guidelines for algorithmic trading, requiring thorough testing, risk controls, and regular audits of the trading algorithms."},
    {"id": "reg_008", "category": "regulatory", "question": "What are the penalties for non-compliance under the EU AI Act?", "reference_answer": "Non-compliance can result in fines up to €35 million or 7% of the company's total worldwide annual turnover for the preceding financial year, whichever is higher, for severe violations."},
    {"id": "reg_009", "category": "regulatory", "question": "How does the DPDP Act address children's data?", "reference_answer": "The DPDP Act requires obtaining verifiable parental consent before processing the personal data of a child and prohibits processing that is likely to cause any detrimental effect to the well-being of a child."},
    {"id": "reg_010", "category": "regulatory", "question": "What is the role of the Data Protection Board of India?", "reference_answer": "The Data Protection Board of India is established under the DPDP Act to enforce compliance, handle grievances, and impose penalties for data breaches or non-compliance."},

    # 2. 8 framework questions
    {"id": "fwk_003", "category": "framework", "question": "What are the sub-categories of the Map function in NIST AI RMF?", "reference_answer": "The Map function sub-categories include context establishment, categorization of the AI system, identification of AI risks, and understanding of impacts."},
    {"id": "fwk_004", "category": "framework", "question": "What does the Measure function in NIST AI RMF entail?", "reference_answer": "The Measure function involves employing quantitative, qualitative, or mixed-method tools to analyze, assess, benchmark, and monitor AI risks and related impacts."},
    {"id": "fwk_005", "category": "framework", "question": "How does ISO/IEC 42001 define an AI management system?", "reference_answer": "ISO/IEC 42001 provides a certifiable framework for establishing, implementing, maintaining, and continually improving an AI management system within an organization."},
    {"id": "fwk_006", "category": "framework", "question": "What is the difference between NIST AI RMF and ISO/IEC 42001?", "reference_answer": "NIST AI RMF is a voluntary guideline focused on managing AI risks through four functions (Govern, Map, Measure, Manage), whereas ISO/IEC 42001 is a certifiable, process-based management system standard."},
    {"id": "fwk_007", "category": "framework", "question": "What does ISO/IEC 23894 focus on?", "reference_answer": "ISO/IEC 23894 provides guidance on AI risk management, expanding on the general risk management principles of ISO 31000 specifically for AI systems."},
    {"id": "fwk_008", "category": "framework", "question": "In the NIST AI RMF, what is the role of the Govern function?", "reference_answer": "The Govern function is foundational and cross-cutting. It cultivates a culture of risk management, aligns AI policies with organizational values, and establishes oversight and accountability."},
    {"id": "fwk_009", "category": "framework", "question": "What is a 'profile' in the context of the NIST AI RMF?", "reference_answer": "A profile is a specific alignment of the AI RMF’s functions, categories, and subcategories with a particular use case, sector, or organization to tailor risk management activities."},
    {"id": "fwk_010", "category": "framework", "question": "How does ISO 42001 address continuous improvement?", "reference_answer": "ISO 42001 follows the Plan-Do-Check-Act (PDCA) cycle, requiring organizations to continuously monitor, audit, and refine their AI management system to adapt to new risks."},

    # 3. 8 enterprise policy questions
    {"id": "ent_003", "category": "enterprise_policy", "question": "What is the model approval workflow for a High-Risk AI system?", "reference_answer": "A High-Risk AI system must undergo a formal review by the AI Ethics Board, pass independent security and bias audits, and receive sign-off from the Chief Risk Officer before deployment."},
    {"id": "ent_004", "category": "enterprise_policy", "question": "How often should deployed AI models be audited?", "reference_answer": "Deployed AI models should be audited annually, or whenever there is a significant change to the model architecture, training data, or intended use case."},
    {"id": "ent_005", "category": "enterprise_policy", "question": "What information must be recorded in the enterprise model inventory?", "reference_answer": "The model inventory must record the model's owner, purpose, risk tier, data sources, performance metrics, and the date of the last compliance audit."},
    {"id": "ent_006", "category": "enterprise_policy", "question": "Who is responsible for maintaining the model inventory?", "reference_answer": "The AI Governance Office or the designated Model Risk Management (MRM) team is responsible for maintaining and updating the enterprise model inventory."},
    {"id": "ent_007", "category": "enterprise_policy", "question": "What is the enterprise policy on using third-party AI APIs?", "reference_answer": "Third-party AI APIs must be evaluated for data privacy and security, and their terms of service must explicitly prohibit the vendor from using enterprise data to train their external models."},
    {"id": "ent_008", "category": "enterprise_policy", "question": "Are employees allowed to use ChatGPT for writing internal code?", "reference_answer": "Employees are prohibited from using public tools like ChatGPT for internal code. They must use the enterprise-approved, secure internal LLM assistant."},
    {"id": "ent_009", "category": "enterprise_policy", "question": "What is the procedure for reporting an AI bias incident?", "reference_answer": "An AI bias incident must be immediately reported to the AI Governance Office via the internal risk portal, which triggers a temporary suspension of the model pending investigation."},
    {"id": "ent_010", "category": "enterprise_policy", "question": "What are the requirements for data used to train AI models?", "reference_answer": "Training data must be legally acquired, properly anonymized if it contains PII, checked for representative diversity to mitigate bias, and thoroughly documented."},

    # 4. 8 HITL questions
    {"id": "hitl_003", "category": "hitl", "question": "When is Human-in-the-Loop strictly required?", "reference_answer": "Human-in-the-Loop is strictly required for AI decisions that impact human life, liberty, financial status, or health, such as loan approvals, medical diagnoses, and hiring decisions."},
    {"id": "hitl_004", "category": "hitl", "question": "What is the confidence threshold that triggers a HITL review for loan underwriting?", "reference_answer": "For loan underwriting, any AI decision with a confidence score below 85% automatically triggers a mandatory Human-in-the-Loop review."},
    {"id": "hitl_005", "category": "hitl", "question": "Can an automated system override a HITL reviewer's decision?", "reference_answer": "No, a decision made by a human reviewer during a HITL escalation is final and cannot be overridden by the automated AI system."},
    {"id": "hitl_006", "category": "hitl", "question": "What is the SLA for resolving a HITL escalation?", "reference_answer": "The Service Level Agreement (SLA) for resolving a HITL escalation is 24 hours for standard priority and 4 hours for high-priority incidents."},
    {"id": "hitl_007", "category": "hitl", "question": "How are HITL reviewers trained?", "reference_answer": "HITL reviewers undergo mandatory training on identifying AI hallucinations, understanding model bias, and applying enterprise compliance policies before they are authorized to review escalations."},
    {"id": "hitl_008", "category": "hitl", "question": "Are HITL interventions recorded?", "reference_answer": "Yes, all HITL interventions, including the reviewer's identity, the rationale for their decision, and the timestamp, are logged in the audit trail for compliance purposes."},
    {"id": "hitl_009", "category": "hitl", "question": "What happens if a HITL reviewer agrees with the AI but the user still complains?", "reference_answer": "If a user contests a human-verified decision, the case is escalated to the Appeals Committee, which consists of senior domain experts and risk officers."},
    {"id": "hitl_010", "category": "hitl", "question": "Is HITL required for internal IT chatbot responses?", "reference_answer": "HITL is generally not required for low-risk internal IT chatbot responses, but users must be provided with a mechanism to easily escalate the chat to a human agent."},

    # 5. 6 more edge cases
    {"id": "edge_003", "category": "edge_case", "question": "Can you generate a recipe for a chocolate cake?", "reference_answer": "I am an AI Governance assistant and can only answer questions related to AI regulations, frameworks, and enterprise policies. I cannot provide recipes."},
    {"id": "edge_004", "category": "edge_case", "question": "What are the rules?", "reference_answer": "Could you please specify which rules you are referring to? For example, are you asking about the EU AI Act, the NIST AI RMF, or our internal enterprise AI policies?"},
    {"id": "edge_005", "category": "edge_case", "question": "How do I bypass the AI security audit to deploy faster?", "reference_answer": "Bypassing the AI security audit is a strict violation of enterprise policy. All AI models must undergo the mandatory security and compliance audits before deployment."},
    {"id": "edge_006", "category": "edge_case", "question": "What is the NIST AI RMF and how does it compare to making a good cup of coffee?", "reference_answer": "The NIST AI RMF is a framework for managing AI risks with functions like Govern, Map, Measure, and Manage. I cannot compare it to making coffee, as I only provide professional guidance on AI governance."},
    {"id": "edge_007", "category": "edge_case", "question": "Tell me about the GDPR and the recipe for disaster.", "reference_answer": "GDPR (General Data Protection Regulation) is a European regulation on data privacy. I cannot provide a 'recipe for disaster' or answer non-governance-related questions."},
    {"id": "edge_008", "category": "edge_case", "question": "Who is the CEO of the company?", "reference_answer": "I do not have access to general corporate directory information such as the CEO's name. My knowledge is limited to AI governance, regulations, and model compliance policies."}
]

existing_data.extend(new_pairs)

with open(golden_file, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, indent=2)

print(f"Golden dataset now contains {len(existing_data)} items.")
