from openai import OpenAI

client = OpenAI(
    # api_key="AIzaSyBWKGlVTGseZFyfgzjeuo4-Lra_sYJhrnA",
    api_key="AIzaSyAcgGGUvybk7xww0Yuk1uoiiKcU0MfQwW0",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

response = client.chat.completions.create(
    model="gemini-2.5-flash-lite",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain LLMs in simple terms"},
    ],
)

print(response.choices[0].message.content)
