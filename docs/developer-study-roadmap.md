# Roadmap de estudo para desenvolvedores

Este guia apresenta a aplicacao em uma ordem de estudo progressiva. Cada etapa
combina o que ja esta implementado com os termos tecnicos que devem ser
pesquisados e praticados.

## Como estudar

1. Leia a secao indicada no codigo.
2. Execute a aplicacao localmente com Docker Compose.
3. Rode os testes relacionados ao assunto.
4. Faca uma pequena alteracao experimental.
5. Registre o que mudou e valide com testes, lint e type checking.

Comandos base:

```bash
pip install -r requirements.txt
pytest -q
ruff check app tests scripts
mypy app tests scripts --ignore-missing-imports --no-error-summary
docker compose config --quiet
```

## Etapa 1: Python e ambiente

### O que estudar

- Python 3.12: tipos, async/await, excecoes, context managers e generators.
- Ambientes virtuais: `venv`, isolamento de dependencias e `requirements.txt`.
- Variaveis de ambiente e arquivos `.env`.
- CLI, exit codes e leitura de logs.
- Git: branch, commit, push, diff e historico.

### Onde observar

- `requirements.txt`
- `.env.example`
- `.gitignore`
- `scripts/benchmark.py`
- `app/core/config.py`

### Termos tecnicos

`Python typing`, `coroutine`, `async iterator`, `Pydantic Settings`, `environment
variable`, `dependency pinning`, `virtual environment`, `semantic versioning`.

## Etapa 2: HTTP, REST e FastAPI

### O que estudar

- HTTP methods, status codes, headers e content types.
- REST resource design e JSON.
- FastAPI routing, dependency injection e request validation.
- Pydantic schemas e OpenAPI.
- Server-Sent Events (SSE) para streaming.

### Onde observar

- `app/main.py`
- `app/api/routes/`
- `app/api/dependencies.py`
- `app/schemas/openai.py`
- `tests/integration/`

### Exercicios

- Adicionar um endpoint protegido.
- Adicionar um campo validado a um schema.
- Testar uma resposta `401`, `404` e `422`.
- Comparar uma resposta normal com uma resposta `text/event-stream`.

### Termos tecnicos

`ASGI`, `middleware`, `dependency injection`, `schema validation`, `OpenAPI`,
`SSE`, `streaming response`, `idempotency`, `HTTP error handling`.

## Etapa 3: Arquitetura da aplicacao

### O que estudar

- Clean Architecture e separacao por camadas.
- Domain, service, infrastructure e API layers.
- Repository Pattern e Service Layer.
- Protocols/interfaces e Dependency Inversion.
- Composition Root e Dependency Injection.

### Onde observar

- `app/domain/interfaces.py`
- `app/services/llm_service.py`
- `app/infrastructure/repositories.py`
- `app/container.py`
- `app/api/dependencies.py`

### Fluxo principal

```text
HTTP request
  -> FastAPI route
  -> dependency injection
  -> service
  -> LLMProvider protocol
  -> provider client HTTP
  -> normalized response
  -> OpenAI-compatible response
```

### Termos tecnicos

`SOLID`, `separation of concerns`, `dependency inversion`, `repository pattern`,
`composition root`, `polymorphism`, `structural typing`, `contract testing`.

## Etapa 4: Contrato OpenAI e providers

### O que estudar

- Contrato de chat completions, completions, embeddings e models.
- Adapter Pattern para APIs com formatos diferentes.
- Normalizacao de payloads e respostas.
- Provider health checks.
- Fallback e classificacao de erros.

### Onde observar

- `app/domain/interfaces.py`
- `app/infrastructure/ollama/`
- `app/infrastructure/openai_compatible/`
- `app/infrastructure/fallback_provider.py`
- `tests/unit/test_provider_contract.py`
- `tests/unit/test_openai_compatible_provider.py`

### Fluxo de fallback

```text
primary provider
  -> ProviderUnavailableError
  -> fallback provider
  -> retry somente antes do primeiro chunk
  -> erro apos streaming iniciado nao e repetido
```

### Termos tecnicos

`provider abstraction`, `adapter pattern`, `OpenAI-compatible API`,
`capability boundary`, `fault isolation`, `failover`, `retry policy`,
`stream replay safety`, `circuit breaker`.

## Etapa 5: Concorrencia e performance

### O que estudar

- Event loop do asyncio.
- Concorrencia versus paralelismo.
- Semaphores e backpressure.
- Connection pooling e keep-alive.
- Latencia, throughput, p50, p95 e p99.
- Time to first byte (TTFB) em streaming.
- Uso de memoria e limites operacionais.

### Onde observar

- `app/api/middleware.py`
- `app/infrastructure/ollama/client.py`
- `app/infrastructure/openai_compatible/client.py`
- `tests/performance/`
- `scripts/benchmark.py`

### Exercicios

- Alterar `INFERENCE_CONCURRENCY_LIMIT` e comparar p95.
- Executar benchmark de `/health/live`.
- Executar benchmark de chat com streaming.
- Comparar `HTTPX_MAX_CONNECTIONS` e `HTTPX_MAX_KEEPALIVE_CONNECTIONS`.

### Termos tecnicos

`asyncio`, `semaphore`, `backpressure`, `bounded concurrency`, `connection pool`,
`load testing`, `latency percentile`, `throughput`, `tail latency`, `memory RSS`.

## Etapa 6: Resiliencia e cache

### O que estudar

- Timeout por operacao.
- Erros transientes e permanentes.
- Cache com TTL e invalidacao.
- Rate limiting local e distribuido.
- Redis e fallback para memoria.
- Health check, liveness e readiness.

### Onde observar

- `app/infrastructure/rate_limiter.py`
- `app/infrastructure/redis_rate_limiter.py`
- `app/infrastructure/repositories.py`
- `app/services/health_service.py`
- `tests/unit/test_model_repository_cache.py`
- `tests/unit/test_rate_limiter.py`

### Termos tecnicos

`TTL`, `cache invalidation`, `sliding window`, `distributed state`, `graceful
degradation`, `readiness probe`, `liveness probe`, `timeout budget`.

## Etapa 7: Seguranca

### O que estudar

- API keys, Bearer authentication e allowlists.
- Secret files e secret rotation.
- CORS e security headers.
- Request body limits e denial of service.
- Rate limiting de requests anonimas.
- Fingerprinting de secrets em logs.
- Principle of least privilege.

### Onde observar

- `app/api/dependencies.py`
- `app/core/config.py`
- `app/api/middleware.py`
- `deploy/scripts/validate-secrets.sh`
- `.gitignore`

### Termos tecnicos

`authentication`, `authorization`, `allowlist`, `CORS`, `CSRF`, `security headers`,
`secret management`, `credential rotation`, `least privilege`, `information leakage`.

## Etapa 8: Observabilidade

### O que estudar

- Structured logging e correlation ID.
- Prometheus metrics e labels.
- Grafana dashboards e alert rules.
- Distributed tracing e OpenTelemetry.
- OTLP, collector e trace backend.
- Correlacao entre logs, metricas e traces.

### Onde observar

- `app/core/logging.py`
- `app/core/metrics.py`
- `app/core/tracing.py`
- `monitoring/prometheus/`
- `monitoring/grafana/`
- `monitoring/otel/collector-config.yml`
- `docker-compose.yml` com profile `tracing`

### Termos tecnicos

`observability`, `structured logging`, `correlation ID`, `RED metrics`,
`Prometheus`, `Grafana`, `OpenTelemetry`, `OTLP`, `span`, `trace context`,
`sampling`, `alerting`.

## Etapa 9: Frontend e experiencia de uso

### O que estudar

- HTML, CSS e JavaScript sem framework.
- Fetch API e consumo de REST.
- SSE no navegador.
- Estado local, localStorage e exportacao JSON.
- Tratamento de loading, erro e cancelamento.

### Onde observar

- `web/index.html`
- `web/app.js`
- `web/styles.css`
- `app/api/routes/web.py`

### Termos tecnicos

`frontend state`, `event stream`, `client-side persistence`, `progressive
enhancement`, `responsive UI`, `accessibility`, `error boundary`.

## Etapa 10: Docker e ambientes

### O que estudar

- Dockerfile e image layers.
- Docker Compose, networks, volumes e profiles.
- Health checks e `depends_on` conditions.
- Imagens versionadas e GHCR.
- Reverse proxy, DNS e TLS automatico.
- Diferenca entre configuracao de desenvolvimento e producao.

### Onde observar

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.yml`
- `Dockerfile`
- `.env.example`

### Termos tecnicos

`container image`, `multi-stage build`, `immutable artifact`, `service discovery`,
`persistent volume`, `reverse proxy`, `TLS termination`, `certificate renewal`,
`environment promotion`.

## Etapa 11: CI/CD e operacao

### O que estudar

- GitHub Actions jobs, steps e quality gates.
- Quality gates: Ruff, mypy, pytest e coverage.
- Build reproducivel e validacao local.
- Smoke tests e benchmark pos-startup.

### Onde observar

- `.github/workflows/ci.yml`
- `docs/production-readiness-checklist.md`

### Termos tecnicos

`CI`, `quality gate`, `artifact`, `Docker build`, `smoke test`, `benchmark`,
`runbook`, `reproducible environment`.

## O que ja esta implementado

- API REST compativel com OpenAI.
- Chat, completions, embeddings e streaming SSE.
- Providers Ollama, LM Studio e vLLM.
- Fallback entre providers.
- Cache, timeouts, concorrencia e rate limiting.
- Redis opcional para rate limiting distribuido.
- UI web local.
- Prometheus, Grafana e alertas basicos.
- OpenTelemetry opcional com Collector e Jaeger local.
- CI, Docker Compose local e validacao automatizada.
- Benchmark de performance e checklist de go-live.

## O que ainda precisa ser validado localmente

- Download dos modelos no Ollama.
- Execucao dos profiles Redis, monitoring e tracing.
- Benchmarks de inferencia com modelos ativos.
- Screenshots e relatorios para o portfolio.

## Projeto final sugerido

Depois de estudar as etapas, o desenvolvedor junior deve conseguir:

1. Adicionar um endpoint com schema, autenticacao e teste.
2. Implementar um provider compatibilizado pelo contrato `LLMProvider`.
3. Diagnosticar uma falha usando logs, metricas e traces.
4. Ajustar concorrencia e pool com base em p95 e throughput.
5. Subir os profiles locais e interpretar metricas e traces.
6. Executar benchmark, analisar resultados e documentar a capacidade local.
