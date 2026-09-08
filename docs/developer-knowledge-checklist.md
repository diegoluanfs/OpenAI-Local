# Checklist de conhecimentos para desenvolver uma aplicacao local de IA

Este documento lista os conhecimentos necessarios para entender, manter e evoluir
uma plataforma local de inferencia de LLMs como o OpenAI Local.

## 1. Fundamentos de programacao

- [ ] Python: funcoes, classes, modulos e pacotes.
- [ ] Tipos estaticos e type hints.
- [ ] Excecoes e tratamento de erros.
- [ ] Context managers.
- [ ] Iterators e generators.
- [ ] Programacao orientada a objetos.
- [ ] Principios SOLID.
- [ ] Leitura de logs e debugging.
- [ ] Linha de comando e exit codes.
- [ ] Git: branch, diff, commit, merge e pull request.

Termos para estudar: `Python typing`, `OOP`, `SOLID`, `exception handling`,
`generator`, `context manager`, `debugging`, `Git workflow`.

## 2. Python assincrono

- [ ] `async` e `await`.
- [ ] Event loop.
- [ ] Coroutines e tasks.
- [ ] `asyncio.gather`.
- [ ] Async iterators.
- [ ] Semaphores e controle de concorrencia.
- [ ] Cancelamento de tasks.
- [ ] Timeouts assincronos.
- [ ] Diferenca entre concorrencia e paralelismo.

Termos para estudar: `asyncio`, `event loop`, `coroutine`, `task`, `async iterator`,
`bounded concurrency`, `backpressure`, `cancellation`.

## 3. HTTP e APIs

- [ ] HTTP methods: GET, POST, PUT e DELETE.
- [ ] Status codes.
- [ ] Headers.
- [ ] JSON.
- [ ] Content types.
- [ ] REST.
- [ ] Autenticacao via Bearer token e API key.
- [ ] CORS.
- [ ] Server-Sent Events.
- [ ] OpenAPI e Swagger.

Termos para estudar: `HTTP`, `REST`, `JSON`, `SSE`, `OpenAPI`, `Swagger UI`,
`content negotiation`, `idempotency`, `HTTP middleware`.

## 4. FastAPI e ASGI

- [ ] Criacao de rotas.
- [ ] Dependency Injection com `Depends`.
- [ ] Pydantic schemas.
- [ ] Validacao de requests.
- [ ] Lifespan da aplicacao.
- [ ] Middleware.
- [ ] Streaming responses.
- [ ] Exception handlers.
- [ ] TestClient e ASGITransport.

Termos para estudar: `FastAPI`, `ASGI`, `Uvicorn`, `Pydantic v2`,
`dependency injection`, `middleware`, `lifespan`, `exception handler`.

## 5. Arquitetura de software

- [ ] Separacao entre API, servicos, dominio e infraestrutura.
- [ ] Clean Architecture.
- [ ] Ports and Adapters.
- [ ] Repository Pattern.
- [ ] Service Layer.
- [ ] Composition Root.
- [ ] Dependency Inversion.
- [ ] Interfaces e Protocols.
- [ ] Testabilidade e baixo acoplamento.

Termos para estudar: `Clean Architecture`, `Hexagonal Architecture`,
`Ports and Adapters`, `Repository Pattern`, `Service Layer`, `Dependency Inversion`,
`composition root`, `separation of concerns`.

## 6. Modelos de linguagem

- [ ] O que e um LLM.
- [ ] Tokens.
- [ ] Context window.
- [ ] Prompt e completion.
- [ ] System, user e assistant messages.
- [ ] Temperature.
- [ ] Max tokens.
- [ ] Streaming de tokens.
- [ ] Embeddings.
- [ ] Modelos de chat versus modelos de embedding.
- [ ] CPU, memoria e GPU na inferencia.

Termos para estudar: `LLM`, `tokenization`, `context window`, `prompt engineering`,
`temperature`, `embedding`, `vector representation`, `inference`, `quantization`.

## 7. Providers de IA

- [ ] API do Ollama.
- [ ] APIs OpenAI-compatible.
- [ ] LM Studio.
- [ ] vLLM.
- [ ] Adapter Pattern.
- [ ] Normalizacao de respostas.
- [ ] Health check de provider.
- [ ] Provider fallback.
- [ ] Erros transientes e permanentes.
- [ ] Limites de capacidade de cada provider.

Termos para estudar: `provider abstraction`, `adapter pattern`, `failover`,
`retry policy`, `fault tolerance`, `capability mapping`, `response normalization`.

## 8. Cache e resiliencia

- [ ] Cache de modelos.
- [ ] TTL.
- [ ] Invalidacao de cache.
- [ ] Timeouts por operacao.
- [ ] Rate limiting.
- [ ] Rate limiting distribuido.
- [ ] Redis.
- [ ] Fallback em memoria.
- [ ] Liveness e readiness.
- [ ] Graceful degradation.

Termos para estudar: `TTL cache`, `cache invalidation`, `sliding window`,
`Redis`, `distributed state`, `health probe`, `timeout budget`, `resilience pattern`.

## 9. Seguranca

- [ ] API keys.
- [ ] Authentication versus authorization.
- [ ] Allowlists.
- [ ] Secret files.
- [ ] Rotacao de secrets.
- [ ] CORS seguro.
- [ ] Security headers.
- [ ] Content Security Policy.
- [ ] Limite de tamanho do request.
- [ ] Rate limiting contra abuso.
- [ ] Nao expor secrets em logs.
- [ ] Principio do menor privilegio.

Termos para estudar: `authentication`, `authorization`, `API key`, `secret management`,
`CORS`, `CSP`, `security headers`, `rate limiting`, `least privilege`, `OWASP`.

## 10. Docker e Docker Compose

- [ ] Imagens e containers.
- [ ] Dockerfile.
- [ ] Layers e build cache.
- [ ] Networks.
- [ ] Volumes persistentes.
- [ ] Environment variables.
- [ ] Health checks.
- [ ] `depends_on`.
- [ ] Compose profiles.
- [ ] Logs e ciclo de vida de containers.
- [ ] Rebuild versus restart.

Termos para estudar: `Docker image`, `container`, `Dockerfile`, `layer cache`,
`Docker network`, `volume`, `healthcheck`, `Compose profile`, `service discovery`.

## 11. Observabilidade

- [ ] Logs estruturados JSON.
- [ ] Correlation ID.
- [ ] Metricas de requests.
- [ ] Contadores, gauges e histograms.
- [ ] Prometheus.
- [ ] PromQL.
- [ ] Grafana.
- [ ] Alertas.
- [ ] OpenTelemetry.
- [ ] OTLP.
- [ ] Traces e spans.
- [ ] Jaeger.
- [ ] Relacao entre logs, metricas e traces.

Termos para estudar: `observability`, `structured logging`, `correlation ID`,
`Prometheus`, `PromQL`, `Grafana`, `OpenTelemetry`, `OTLP`, `trace`, `span`,
`sampling`, `SRE golden signals`.

## 12. Performance

- [ ] Latencia.
- [ ] Throughput.
- [ ] p50, p95 e p99.
- [ ] Time to First Byte.
- [ ] Connection pooling.
- [ ] Keep-alive.
- [ ] Concorrencia limitada.
- [ ] Uso de memoria RSS.
- [ ] Testes de carga.
- [ ] Analise de gargalos.
- [ ] Benchmark reproduzivel.

Termos para estudar: `latency percentile`, `tail latency`, `throughput`, `TTFB`,
`connection pool`, `load testing`, `profiling`, `memory RSS`, `bottleneck analysis`.

## 13. Testes e qualidade

- [ ] Testes unitarios.
- [ ] Testes de integracao.
- [ ] Testes de contrato.
- [ ] Testes de streaming.
- [ ] Testes de timeout.
- [ ] Testes de concorrencia.
- [ ] Mocks e fakes.
- [ ] Cobertura de testes.
- [ ] Ruff.
- [ ] mypy.
- [ ] CI quality gates.

Termos para estudar: `pytest`, `pytest-asyncio`, `fixture`, `mock`, `fake`,
`contract test`, `integration test`, `test coverage`, `static type checking`, `lint`.

## 14. Frontend local

- [ ] HTML sem framework.
- [ ] CSS responsivo.
- [ ] JavaScript moderno.
- [ ] Fetch API.
- [ ] SSE no navegador.
- [ ] DOM e eventos.
- [ ] Estado local.
- [ ] `localStorage`.
- [ ] Tratamento de loading e erros.
- [ ] Acessibilidade basica.

Termos para estudar: `Fetch API`, `EventSource`, `DOM`, `client-side state`,
`localStorage`, `responsive design`, `accessibility`, `progressive enhancement`.

## 15. Como estudar este repositorio

1. Suba apenas API e Ollama.
2. Teste `/health/live` e `/health/ready`.
3. Abra `/docs` e explore o OpenAPI.
4. Faca uma chamada de chat com API key.
5. Ative streaming.
6. Teste embeddings.
7. Suba Redis e observe o rate limiting.
8. Suba Prometheus e Grafana.
9. Suba Jaeger e o OpenTelemetry Collector.
10. Execute os testes.
11. Execute o benchmark.
12. Leia os logs durante uma requisicao.
13. Troque o provider.
14. Configure fallback.
15. Estude o fluxo completo de uma requisicao.

## 16. O que a pessoa deve conseguir fazer ao final

- Adicionar uma nova rota FastAPI com schema e testes.
- Criar um novo adapter de provider.
- Explicar o fluxo de uma requisicao do HTTP ao modelo.
- Diagnosticar uma falha usando logs, metricas e traces.
- Ajustar timeouts, concorrencia e pool HTTP.
- Identificar problemas de API key e configuracao.
- Subir e reiniciar os servicos Docker.
- Medir performance com p95, p99 e throughput.
- Evoluir a interface sem quebrar o contrato da API.
- Implementar uma melhoria seguindo os quality gates do projeto.

## 17. Ordem recomendada de aprendizado

1. Python e Git.
2. HTTP e FastAPI.
3. AsyncIO.
4. Clean Architecture.
5. Docker Compose.
6. LLMs e providers.
7. Testes.
8. Seguranca.
9. Redis e resiliencia.
10. Observabilidade.
11. Performance.
12. Frontend e streaming.
