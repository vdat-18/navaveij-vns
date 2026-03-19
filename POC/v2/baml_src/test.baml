// LLM Health Check Test
// Verifies that the credentials in .env produce valid responses

function HealthCheck() -> HealthCheckResult {
  client NavaveijClient
  prompt #"
    {{ _.role("system") }}
    You are a health check assistant. Respond with valid JSON only.
    {{ _.role("user") }}
    Respond with a JSON object containing:
    - "status": "ok" if you can process this request
    - "model": the model name you are using
    - "timestamp": current ISO timestamp
    Just output the JSON, nothing else.
  "#
}

// Structured output for health check results
class HealthCheckResult {
  status string
  model string
  timestamp string
}

test LLMHealthCheck {
  functions [HealthCheck]
  args {
  }
  // Verify we got a valid response with status "ok"
  @@assert( {{ this.status == "ok" }} )
  // Verify model is returned
  @@assert( {{ this.model|length > 0 }} )
  // Verify timestamp is returned
  @@assert( {{ this.timestamp|length > 0 }} )
}

// Simple smoke test for quick validation
function CredentialSmokeTest() -> string {
  client NavaveijClient
  prompt #"
    {{ _.role("system") }}
    You are a test assistant.
    {{ _.role("user") }}
    Reply with exactly: PONG
  "#
}

test CredentialsWork {
  functions [CredentialSmokeTest]
  args {
  }
  @@assert( {{ this|trim == "PONG" }} )
}
