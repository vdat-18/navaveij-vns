// BAML Clients Configuration
//
// TrollLLM is a Claude API proxy (ANTHROPIC_BASE_URL=https://chat.trollllm.xyz).
// It accepts the native Anthropic API request/response format.
// BAML's 'anthropic' provider is therefore the correct choice:
//   - Sends messages in Anthropic format (no json_schema, no system-only issues)
//   - Parses the Anthropic-format response (no missing "index" field issue)
//   - Reads from LLM_API_KEY (the TrollLLM key) and LLM_BASE_URL (the proxy URL)
//
// load_dotenv() in main.py MUST run before baml_client is imported so
// LLM_API_KEY / LLM_BASE_URL / LLM_MODEL are captured at BAML runtime init.

client<llm> NavaveijClient {
  provider anthropic
  options {
    api_key env.LLM_API_KEY
    base_url env.LLM_BASE_URL
    model env.LLM_MODEL
  }
}