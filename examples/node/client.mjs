import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "dummy",
});

const response = await client.chat.completions.create({
  model: "llama3.2:3b",
  messages: [
    { role: "system", content: "Responda em pt-BR." },
    { role: "user", content: "Liste 3 usos para embeddings." },
  ],
});

console.log(response.choices[0].message.content);
