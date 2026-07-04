from openai import OpenAI


client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy",  # opcional se API_KEY estiver vazio no servidor
)

response = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[
        {"role": "system", "content": "Responda em pt-BR."},
        {"role": "user", "content": "Explique Clean Architecture em uma frase."},
    ],
)

print(response.choices[0].message.content)
