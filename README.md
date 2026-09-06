# Local LLM Server

Servidor de IA local com API REST compativel com a OpenAI, usando FastAPI + Ollama.

## Visao Geral

- Execucao 100% local e offline apos download dos modelos
- Endpoints OpenAI-like: `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`
- Gerenciamento de modelos: listagem, modelo padrao, pull e status
- Health check com estado da API e Ollama
- Interface web local para chat e operacao
- Rate limiting em memoria ou Redis
- Metricas Prometheus e CI com quality gates
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
    rate_limiter.py
    redis_rate_limiter.py
  services/
  schemas/
web/
  index.html
  app.js
  styles.css
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

- `APP_ENV` (padrao: `development`; valores: `development`, `test`, `production`)
- `HOST` (padrao: `0.0.0.0`)
- `PORT` (padrao: `8000`)
- `OLLAMA_URL` (padrao: `http://ollama:11434`)
- `DEFAULT_MODEL` (padrao: `llama3.2:3b`)
- `EMBEDDING_MODEL` (padrao: `nomic-embed-text`)
- `LOG_LEVEL` (padrao: `INFO`)
- `TIMEOUT_SECONDS` (padrao: `120`)
- `TIMEOUT_TAGS_SECONDS` (padrao: `10`)
- `TIMEOUT_CHAT_SECONDS` (padrao: `120`)
- `TIMEOUT_GENERATE_SECONDS` (padrao: `120`)
- `TIMEOUT_EMBEDDINGS_SECONDS` (padrao: `60`)
- `TIMEOUT_PULL_SECONDS` (padrao: `0`, sem timeout)
- `MODEL_CACHE_TTL_SECONDS` (padrao: `5`)
- `API_KEY` (opcional)
- `CORS_ORIGINS` (padrao: `*`)
- `RATE_LIMIT_PER_MINUTE` (padrao: `0`, desabilitado)
- `AUTO_PULL_DEFAULT_MODEL` (padrao: `true`)
- `ALLOWED_API_KEYS` (obrigatorio em `production`; separado por virgulas)
- `ALLOW_ANONYMOUS_REQUESTS` (padrao: `true`; forcado para `false` em `production`)
- `UNAUTH_RATE_LIMIT_PER_MINUTE` (padrao: `30`)
- `MAX_REQUEST_BODY_BYTES` (padrao: `1048576` / 1 MiB)
- `INFERENCE_CONCURRENCY_LIMIT` (padrao: `2`)
- `RATE_LIMIT_BACKEND` (padrao: `memory`; valores: `memory`, `redis`)
- `REDIS_URL` (opcional; necessario quando `RATE_LIMIT_BACKEND=redis`)
- `REDIS_KEY_PREFIX` (padrao: `local-llm:ratelimit`)

## Uso

Base URL local:

`http://localhost:8000/v1`

Interface web:

`http://localhost:8000/`

A interface oferece chat direto com o modelo local, selecao de modelo, API key opcional, status do Ollama, memoria usada, metricas operacionais e tempo da ultima resposta.

Recursos da interface:

- streaming opcional de respostas
- historico local limitado a 100 mensagens
- exportacao da conversa em JSON
- modelo e modo streaming lembrados no navegador
- API Key mantida somente em memoria, sem ser salva no `localStorage`
- limpeza manual da conversa

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
- `GET /metrics` (Prometheus)

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

- Interface web: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Docker

Servicos no `docker-compose.yml`:

- `ollama`: runtime de modelos locais
- `local-llm-server`: API FastAPI
- `redis`: opcional, habilitado pelo profile `redis`

Os containers `ollama` e `local-llm-server` possuem health checks no Compose.

Volume persistente:

- `ollama_data` para manter os modelos baixados entre reinicializacoes
- `redis_data` para manter o estado do Redis quando o profile estiver ativo

Ao subir pela primeira vez, a API tenta baixar automaticamente o `DEFAULT_MODEL` se ele nao estiver instalado.

Execucao padrao (rate limit em memoria):

```bash
docker compose up --build -d
```

Execucao com Redis (rate limit compartilhado):

```bash
docker compose --profile redis up --build -d
```

Para usar o Redis na API, configure `RATE_LIMIT_BACKEND=redis` e `REDIS_URL=redis://redis:6379/0` no `.env`.

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
- Allowlist configuravel de API Keys para autorizacao (`ALLOWED_API_KEYS`)
- Suporte a API Key via `Authorization: Bearer <key>` ou `X-API-Key`
- Requisicoes sem API key sao permitidas, mas limitadas por `UNAUTH_RATE_LIMIT_PER_MINUTE`
- Inferencias simultaneas limitadas por `INFERENCE_CONCURRENCY_LIMIT`
- Headers HTTP de seguranca para browser e API
- Limite configuravel de tamanho do corpo das requisicoes
- Logs registram apenas fingerprint da API Key, nunca a chave original
- CORS configuravel
- Rate limit em memoria (opcional)

### Producao

Configure as chaves fora do repositorio e use `APP_ENV=production`:

```env
APP_ENV=production
ALLOWED_API_KEYS=chave-secreta-1,chave-secreta-2
ALLOW_ANONYMOUS_REQUESTS=false
```

A aplicacao nao inicia em producao sem pelo menos uma chave configurada. Requisicoes sem API key recebem `401 API Key is required`.

### Rate limit distribuido

Para usar Redis em ambientes com mais de uma instancia, configure:

```env
RATE_LIMIT_BACKEND=redis
REDIS_URL=redis://redis:6379/0
```

Suba o profile Redis com:

```bash
docker compose --profile redis up --build -d
```

O servico `redis` usa o volume `redis_data` e possui health check proprio.

Se o Redis estiver indisponivel, o backend usa automaticamente o rate limiter em memoria como fallback para preservar a disponibilidade local.

## Metricas

O endpoint `GET /metrics` expoe metricas no formato Prometheus:

- total de requisicoes por metodo, rota e status
- duracao das requisicoes
- total de requisicoes de inferencia
- total de tokens por modelo e tipo (`prompt` ou `completion`)
- total de respostas HTTP com erro por rota e status

Configuracao:

- `INFERENCE_CONCURRENCY_LIMIT` (padrao: `2`)

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

### Sprints concluidas

#### Sprint 1: Operacao e erros

- Error envelope padronizado.
- Correlation ID via `X-Request-Id`.
- Logs estruturados e tempo de resposta.
- `/health`, `/health/live` e `/health/ready`.

#### Sprint 2: Cache e resiliencia do provider

- Cache de modelos com TTL e invalidacao apos pull.
- Timeouts por operacao do Ollama.
- Fallback de erro do provider.
- Testes de contrato OpenAPI.

#### Sprint 3: Observabilidade, concorrencia e CI

- `/metrics` com Prometheus.
- Metricas de requests, latencia, inferencia, tokens e erros.
- Limite de concorrencia para inferencia.
- CI com build Docker, OpenAPI, Ruff, mypy, testes e cobertura.

#### Sprint 4: Seguranca e hardening

- Allowlist configuravel de API Keys.
- Exigencia de chaves em producao.
- Rate limit anonimo e headers `Retry-After`.
- Limite de payload.
- Headers HTTP de seguranca.
- Fingerprint de API Key nos logs, sem expor o segredo.

#### Sprint 5: Qualidade automatizada

- Ruff no CI.
- Mypy no CI.
- Cobertura minima de 70%.
- Relatorio `coverage.xml` como artefato da CI.

#### Sprint 6: Rate limit distribuido

- Contrato `RateLimiter` desacoplado.
- Backend em memoria para desenvolvimento.
- Backend Redis opcional com fallback em memoria.
- Profile Docker `redis` com volume e health check.
- Testes unitarios e integracao Redis opt-in via `REDIS_URL`.

#### Sprint 7: Interface web

- Chat local servido em `/`.
- Selecao e refresh de modelos.
- Streaming SSE opcional.
- Historico local limitado a 100 mensagens.
- Exportacao local em JSON.
- Preferencias locais de modelo e streaming.
- Metricas operacionais na interface.
- Atualizacao automatica de health, modelos e metricas.

#### Sprint 8: Metricas operacionais

- Tokens por modelo e tipo (`prompt`/`completion`).
- Erros por rota e status HTTP.
- Taxa de erro exibida na interface.

### Proximas sprints

#### Sprint 9: Performance e testes avancados

- Testes de carga e concorrencia.
- Testes de streaming e timeout.
- Relatorios de performance.
- Otimizacao de pool HTTP e uso de memoria.

#### Sprint 10: Providers alternativos

- Testes de conformidade do contrato `LLMProvider`.
- Provider para LM Studio ou vLLM.
- Selecao de provider por ambiente.
- Fallback entre providers.

#### Sprint 11: Deploy e operacao de producao

Implementado parcialmente:

- Workflow de release em `.github/workflows/release.yml`.
- Publicacao automatica de imagens no GHCR para tags `v*`.
- Tags versionadas e tag `latest`.
- Health check da imagem Docker na CI.

Pendente:

- Ambientes de staging e producao.
- Rollback automatizado.
- TLS via reverse proxy.
- Gestao externa de secrets.
- Grafana, alertas e tracing distribuido.

Regras Prometheus iniciais estao versionadas em `monitoring/prometheus/alerts.yml` para:

- API indisponivel
- taxa de erro acima de 5%
- latencia p95 acima de 10 segundos
- falhas de readiness

## Testes

Executar testes localmente:

```bash
pip install -r requirements.txt
pytest -q
```

O teste de integracao Redis e opt-in. Para executa-lo contra um Redis acessivel:

```powershell
$env:REDIS_URL="redis://localhost:6379/0"
pytest tests/integration/test_redis_integration.py -q
```

## CI

O workflow `.github/workflows/ci.yml` executa automaticamente em pushes e pull requests para `main`:

- compilacao do codigo Python
- lint com Ruff
- verificacao de tipos com mypy
- testes automatizados
- relatorio de cobertura de testes (`coverage.xml`)
- cobertura minima exigida de 70%
- validacao das rotas principais no OpenAPI
- build da imagem Docker

O endpoint operacional `/metrics` continua disponivel em runtime, mas fica oculto da lista do Swagger.

## Release de Imagem

Para publicar uma imagem no GitHub Container Registry, crie e envie uma tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

O workflow publica:

```text
ghcr.io/diegoluanfs/openai-local:v1.0.0
ghcr.io/diegoluanfs/openai-local:latest
```

## Exemplos de Integracao

- Python: `examples/python/client.py`
- Node.js: `examples/node/client.mjs`
- C#: `examples/csharp/Program.cs`

Todos mostram o mesmo principio: trocar apenas `base_url` para `http://localhost:8000/v1`.
