// Safety Critic Validation Function

function ValidateRecommendation(context: string, recommendation: string) -> SafetyCheckResponse {
  client NavaveijClient
  prompt #"
    You are a Senior Clinical Auditor. Review a generated medical recommendation for safety and consistency.

    ### INPUT DATA:
    1. **Raw Clinical Context**: 
    {{ context }}

    2. **AI Recommendation**: 
    {{ recommendation }}

    ### YOUR MISSION:
    Analyze for:
    1. **Clinical Contradictions**: Does it recommend something specifically excluded?
    2. **Omission of Critical Care**: Did it miss a vital test given the signals?
    3. **Internal Logic**: Does the reasoning explain the chosen tier and tests accurately?

    {{ ctx.output_format }}
  "#
}
