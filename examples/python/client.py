import os

from openai import OpenAI


api_key = os.getenv("LOCAL_LLM_API_KEY") or os.getenv("API_KEY")
if not api_key:
    raise RuntimeError("Set LOCAL_LLM_API_KEY or API_KEY before running the example.")

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key=api_key,
)

response = client.chat.completions.create(
    model=os.getenv("LOCAL_LLM_MODEL") or os.getenv("DEFAULT_MODEL", "llama3.2:3b"),
    messages=[
        {"role": "system", "content": "Responda em pt-BR."},
        {"role": "user", "content": "Explique Clean Architecture em uma frase."},
    ],
)

print(response.choices[0].message.content)
