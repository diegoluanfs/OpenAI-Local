# Local LLM Server

Servidor de IA local com API REST compativel com a OpenAI, usando FastAPI + Ollama.

## Visao Geral

- Execucao 100% local e offline apos download dos modelos
- Endpoints OpenAI-like: `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`
- Gerenciamento de modelos: listagem, modelo padrao, pull e status
- Health check com estado da API e Ollama
- Arquitetura desacoplada para trocar provider no futuro
- Docker Compose com persistencia de modelos

## Arquitetura

Padroes utilizados:

- Clean Architecture
- SOLID
- Repository Pattern
- Service Layer
- Dependency Injection (via container + Depends)

Estrutura principal:

```text
app/
  api/
    routes/
  core/
  domain/
  infrastructure/
    ollama/
  services/
  schemas/
  main.py
```

## Requisitos

- Docker e Docker Compose
- Opcional para execucao local sem Docker: Python 3.12+

## Instalacao

1. Clone o repositorio.
2. Crie o arquivo `.env` com base no `.env.example`.

```bash
cp .env.example .env
```

3. Suba o ambiente.

```bash
docker compose up --build
```

## Configuracao

Variaveis suportadas:

- `HOST` (padrao: `0.0.0.0`)
- `PORT` (padrao: `8000`)
- `OLLAMA_URL` (padrao: `http://ollama:11434`)
- `DEFAULT_MODEL` (padrao: `llama3.2:3b`)
- `EMBEDDING_MODEL` (padrao: `nomic-embed-text`)
- `LOG_LEVEL` (padrao: `INFO`)
- `TIMEOUT_SECONDS` (padrao: `120`)
- `API_KEY` (opcional)
- `CORS_ORIGINS` (padrao: `*`)
- `RATE_LIMIT_PER_MINUTE` (padrao: `0`, desabilitado)
- `AUTO_PULL_DEFAULT_MODEL` (padrao: `true`)

## Uso

Base URL local:

`http://localhost:8000/v1`

Compatibilidade: para clientes que usam `https://api.openai.com/v1`, basta trocar `base_url` e, se necessario, chave.

### Endpoint publico sem login

Se quiser um endpoint simples para perguntas diretas, sem API key e sem token, use:

- `POST /ask`

Exemplo:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explique Clean Architecture em uma frase",
    "system_prompt": "Responda em portugues, de forma objetiva"
  }'
```

Resposta esperada:

```json
{
  "question": "Explique Clean Architecture em uma frase",
  "answer": "...",
  "model": "llama3.2:3b",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Endpoints

- `POST /v1/chat/completions`
- `POST /v1/completions`
- `POST /v1/embeddings`
- `GET /v1/models`
- `GET /v1/models/default`
- `PUT /v1/models/default`
- `POST /v1/models/pull`
- `GET /v1/models/status?model=...`
- `GET /health`
- `GET /health/live`
- `GET /health/ready`

### Exemplo Chat Completion

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "system", "content": "Responda em portugues."},
      {"role": "user", "content": "Explique o que e FastAPI."}
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }'
```

### Streaming

Defina `"stream": true` no payload para receber `text/event-stream` no estilo OpenAI.

## Swagger e OpenAPI

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Docker

Servicos no `docker-compose.yml`:

- `ollama`: runtime de modelos locais
- `local-llm-server`: API FastAPI

Volume persistente:

- `ollama_data` para manter os modelos baixados entre reinicializacoes

Ao subir pela primeira vez, a API tenta baixar automaticamente o `DEFAULT_MODEL` se ele nao estiver instalado.

## Troca de Modelo

1. Baixar modelo:

```bash
curl -X POST http://localhost:8000/v1/models/pull \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b"}'
```

2. Definir modelo padrao:

```bash
curl -X PUT http://localhost:8000/v1/models/default \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b"}'
```

## Atualizacao

```bash
docker compose down
docker compose pull
docker compose up --build -d
```

## Logs e Seguranca

- Logs estruturados JSON
- Correlation ID por request (`X-Request-Id`)
- Suporte opcional a API Key (`Authorization: Bearer <key>` ou `X-API-Key`)
- CORS configuravel
- Rate limit em memoria (opcional)

## Contrato de Erro

Erros da API sao retornados no formato padrao:

```json
{
  "error": {
    "message": "Model 'string' not found in Ollama.",
    "type": "local_llm_error",
    "code": "bad_request",
    "request_id": "uuid",
    "path": "/ask",
    "timestamp": "2026-01-01T00:00:00+00:00"
  }
}
```

## Roadmap de Sprints

### Sprint 1 (concluida)

- Error envelope padronizado em todos os handlers globais
- Correlation ID por request com header de resposta `X-Request-Id`
- Endpoints operacionais `GET /health/live` e `GET /health/ready`

### Sprint 2 (proxima)

- Cache de status/lista de modelos com invalidação simples
- Timeouts por operacao de provider e fallback de erro mais especifico
- Testes de contrato OpenAPI para `/ask` e `/v1/chat/completions`

### Sprint 3

- Metricas Prometheus (latencia, taxa de erro, requests, tokens)
- Limites de concorrencia por endpoint para proteger Ollama
- Pipeline CI com validação de schema OpenAPI e smoke tests HTTP

## Testes

Executar testes localmente:

```bash
pip install -r requirements.txt
pytest -q
```

## Exemplos de Integracao

- Python: `examples/python/client.py`
- Node.js: `examples/node/client.mjs`
- C#: `examples/csharp/Program.cs`

Todos mostram o mesmo principio: trocar apenas `base_url` para `http://localhost:8000/v1`.
