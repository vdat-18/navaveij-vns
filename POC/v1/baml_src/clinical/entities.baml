// Clinical Entities and Enums

enum CheckupTier {
  Standard
  Advanced
  Premium
}

class RecommendationResponse {
  ai_recommended_tier CheckupTier
  reasoning_trace string @description("Detailed medical rationale for the selection.")
  additional_tests string[] @description("List of specific tests to add based on signals")
  confidence_score float
  follow_up_advice string
}

class SafetyCheckResponse {
  is_safe bool
  critic_score float
  findings string[]
  suggested_correction string?
}
