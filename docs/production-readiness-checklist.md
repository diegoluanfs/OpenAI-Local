# Checklist de prontidao local

## Execucao

- [ ] Python 3.12 e Docker Compose estao instalados.
- [ ] `.env` foi criado a partir de `.env.example`.
- [ ] `docker compose config --quiet` passa.
- [ ] API e Ollama sobem com `docker compose up --build -d`.
- [ ] `/health/live` retorna 200.
- [ ] `/health/ready` retorna 200 com o modelo instalado.
- [ ] `/docs` e a interface web carregam.

## Funcionalidade

- [ ] `/v1/models` lista os modelos instalados.
- [ ] Chat normal funciona.
- [ ] Chat com streaming SSE funciona.
- [ ] Embeddings funcionam.
- [ ] `/ask` funciona.
- [ ] Troca de provider local foi validada quando disponivel.
- [ ] Fallback local foi exercitado quando configurado.

## Seguranca local

- [ ] API keys nao estao versionadas.
- [ ] `ALLOW_ANONYMOUS_REQUESTS` esta adequado ao objetivo local.
- [ ] CORS esta restrito quando a interface esta separada.
- [ ] Limite de payload e rate limiting foram testados.
- [ ] Logs nao exibem chaves originais.

## Observabilidade

- [ ] Prometheus coleta `/metrics`.
- [ ] Grafana carrega o dashboard operacional.
- [ ] Jaeger recebe traces quando o profile `tracing` esta ativo.
- [ ] Logs, metricas e traces podem ser correlacionados por `X-Request-Id`.
- [ ] Alertas locais foram revisados.

## Performance

- [ ] Ruff, mypy e pytest passam.
- [ ] Benchmark de health foi executado.
- [ ] Benchmark de chat/streaming foi executado com modelo ativo.
- [ ] Throughput, p95/p99, TTFB e memoria foram registrados.
- [ ] Limites de concorrencia e pool foram documentados.

## Portfolio

- [ ] README explica arquitetura e como executar localmente.
- [ ] Screenshots da UI, Grafana e Jaeger foram capturadas.
- [ ] Um relatorio JSON de benchmark foi preservado.
- [ ] O fluxo offline e a privacidade local estao destacados.
