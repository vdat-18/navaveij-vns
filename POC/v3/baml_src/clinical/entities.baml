// Clinical Entities and Enums
// Note: The Tier enum is defined in recommendation_output.baml and shared across this domain.

class RecommendationResponse {
  ai_recommended_tier Tier
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
