// BAML Clients Configuration

// Primary Orchestrator Client — openai-generic for TrollLLM / any custom OpenAI-compatible proxy
// Use openai-generic (not openai) to bypass model validation and support non-OpenAI model names
client<llm> NavaveijClient {
  provider openai-generic
  options {
    base_url env.LLM_BASE_URL
    api_key env.LLM_API_KEY
    model env.LLM_MODEL
  }
}
