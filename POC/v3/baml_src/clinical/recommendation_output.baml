// Multi-Agent Clinical Recommendation System
// Based on 3-Agent Architecture: Risk Analysis -> Rule Matching -> Communication Composition

enum Tier {
  Standard
  Advanced
  Premium
}

enum PriorityLevel {
  Red
  Orange
  Yellow
  Green
}

// ── AGENT 1: CLINICAL RISK ANALYZER ────────────────────────────────────────

class ClinicalRiskProfile {
  primary_risks string[]
  severity_assessment string
  biomarker_interpretation string
  clinical_summary_bullets string[]
  suggested_tier Tier? // AI-led preliminary tiering based on medical risk
  supporting_signal_ids string[]
  missing_signal_ids string[]
}

function AnalyzeClinicalRisks(
  clinical_signals: string,
  biomarker_trends: string,
  hard_constraints: string,
  program_ruleset: string
) -> ClinicalRiskProfile {
  client NavaveijClient
  prompt #"
    You are a Senior Medical Consultant AI. Your task is to analyze raw patient data 
    and produce a high-level clinical risk profile. Do NOT consider hospital prices or 
    package names yet. FOCUS ONLY ON MEDICAL RISK.

    ── INPUT DATA ─────────────────────────────────────────────────────────────
    HARD CONSTRAINTS: {{ hard_constraints }}
    CLINICAL SIGNALS: {{ clinical_signals }}
    BIOMARKER TRENDS: {{ biomarker_trends }}
    HOSPITAL PROGRAM RULESET: {{ program_ruleset }}

    ── INSTRUCTIONS ───────────────────────────────────────────────────────────
    1. Identify the top 3-5 primary clinical risks (e.g., "**Active Hypertension**", "**Obesity**").
    2. Provide a severity assessment (Low/Moderate/High) and justify it medically.
    3. Determine a 'suggested_tier' (Standard, Advanced, or Premium) by evaluating
       the clinical findings against the 'tier_selection_rules' in the hospital ruleset.
       Use these rules as a baseline for clinical severity at Navavej hospital.
    4. Interpret biomarker trends (e.g., "**eGFR is declining** at a rate of 5.5 mL/min/year").
    5. Create a concise list of clinical findings for a physician.
    6. List relevant signal IDs that support your findings in supporting_signal_ids.

    ── FORMATTING ─────────────────────────────────────────────────────────────
    - Use Markdown bolding (**text**) ONLY for important clinical terms, biomarkers, and key diagnoses.
    - Write as a natural paragraph for the summary.
    - Be concise and professional.
    - NO greetings or conversational filler.

    {{ ctx.output_format }}
  "#
}

// ── AGENT 2: POLICY & PACKAGE RESOLVER ─────────────────────────────────────

class AddOnItem {
  item_code string
  priority_level PriorityLevel
  rationale string
}

class RecommendationPlan {
  ai_recommended_tier Tier
  tier_deviation_justification string?
  selected_add_ons AddOnItem[]
  policy_reasoning string
}

function MatchProgramRules(
  risk_profile: ClinicalRiskProfile,
  program_ruleset: string
) -> RecommendationPlan {
  client NavaveijClient
  prompt #"
    You are a Hospital Program Director AI. Your task is to match a patient's 
    Clinical Risk Profile with the hospital's specific Program Ruleset.

    ── INPUT DATA ─────────────────────────────────────────────────────────────
    CLINICAL RISK PROFILE: {{ risk_profile }}
    PROGRAM RULESET: {{ program_ruleset }}

    ── INSTRUCTIONS ───────────────────────────────────────────────────────────
    1. Determine the optimal Final Tier (Standard, Advanced, or Premium).
       - Evaluate the 'suggested_tier' from the Risk Profile.
       - Compare it against the 'tier_selection_rules' and 'rule_preliminary_tier' in the ruleset.
       - You have the authority to OVERRIDE the rule-based preliminary tier if the 
         Clinical Risk Profile shows medical complexity that the rules missed.
    2. Select Add-on Items from the 'add_on_library' in the ruleset.
       - Trigger an add-on ONLY if the patient's supporting_signal_ids intersect with the trigger_signals in the library.
       - Assign Priority: Red (Urgent/Overdue), Orange (Moderate), Yellow (Indicated), Green (Optional).
    3. Write 'policy_reasoning' explaining why this specific package combination was chosen.

    {{ ctx.output_format }}
  "#
}

// ── AGENT 3: CLINICAL COMMUNICATOR ──────────────────────────────────────────

class CommunicationScript {
  clinical_conclusion string
  health_summary string
  recommendation_explanation string
  add_on_highlights string[]
  next_steps string
}

class FinalRecommendation {
  plan RecommendationPlan
  script CommunicationScript
}

function ComposeRecommendation(
  risk_profile: ClinicalRiskProfile,
  recommendation_plan: RecommendationPlan
) -> FinalRecommendation {
  client NavaveijClient
  prompt #"
    You are a Patient Communication Specialist AI. Your task is to draft 
    a professional consultation script based on the Clinical Risk Profile 
    and the finalized Recommendation Plan.

    ── INPUT DATA ─────────────────────────────────────────────────────────────
    RISK PROFILE: {{ risk_profile }}
    RECOMMENDATION PLAN: {{ recommendation_plan }}

    ── INSTRUCTIONS ───────────────────────────────────────────────────────────
    1. Draft a 'clinical_conclusion' (1 sentence high-level summary, use **bolding** for the main diagnosis).
    2. Write a 'health_summary' (concise paragraph) starting directly with the most significant findings.
    3. Explain the reasoning for the chosen Tier and selected Add-ons.
    4. Provide actionable 'next_steps' (concise paragraph).

    ── CONSTRAINTS (MANDATORY) ───────────────────────────────────────────────
    1. NO greetings like "Hello" or "Dear patient".
    2. NO conversational filler or small talk.
    3. Use Markdown bolding (**text**) ONLY for important clinical terms, medications, and key risk factors.
    4. Write as clean paragraphs (prose). 
    5. STRICTLY FORBIDDEN: Do NOT use bullet markers ('-','*') or numbered lists ('1.', '2.', '(1)') anywhere in health_summary or next_steps. Write only full sentences.
    6. Professional, direct, and empathetic medical English.

    {{ ctx.output_format }}
  "#
}
