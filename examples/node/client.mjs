const apiKey = process.env.LOCAL_LLM_API_KEY || process.env.API_KEY;
if (!apiKey) {
  throw new Error("Set LOCAL_LLM_API_KEY or API_KEY before running the example.");
}

import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey,
});

const response = await client.chat.completions.create({
  model: process.env.LOCAL_LLM_MODEL || process.env.DEFAULT_MODEL || "llama3.2:3b",
  messages: [
    { role: "system", content: "Responda em pt-BR." },
    { role: "user", content: "Liste 3 usos para embeddings." },
  ],
});

console.log(response.choices[0].message.content);
