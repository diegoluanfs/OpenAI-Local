# Manual de execucao local

Este manual descreve como clonar, configurar, executar e validar o OpenAI Local
em uma maquina Windows, macOS ou Linux.

## 1. Pre-requisitos

Instale:

- Git
- Docker Desktop ou Docker Engine com Docker Compose
- Python 3.12, opcional para executar testes fora do container
- Ollama, opcional quando a API for executada fora do Docker

Confirme as instalacoes:

```bash
git --version
docker --version
docker compose version
python --version
```

O projeto suporta Python 3.12. Em Windows, use o launcher `py -3.12` quando
`python` apontar para outra versao.

## 2. Clonar o repositorio

```bash
git clone https://github.com/diegoluanfs/OpenAI-Local.git
cd OpenAI-Local
```

## 3. Criar a configuracao

Copie o exemplo:

```powershell
Copy-Item .env.example .env
```

```bash
cp .env.example .env
```

Para o fluxo Docker padrao, mantenha:

```env
APP_ENV=development
OLLAMA_URL=http://ollama:11434
DEFAULT_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text
PROVIDER_NAME=ollama
RATE_LIMIT_BACKEND=memory
```

Para proteger a API com uma chave, gere uma chave aleatoria e configure:

```env
API_KEY=sua-chave-local
ALLOWED_API_KEYS=sua-chave-local
```

Nao versione o arquivo `.env` nem compartilhe a chave.

## 4. Subir a aplicacao com Docker

Construa a imagem e inicie a API com Ollama:

```bash
docker compose up --build -d
```

Verifique os servicos:

```bash
docker compose ps
```

A API fica em `http://localhost:8000` e o Ollama em
`http://localhost:11434`.

A primeira inicializacao pode demorar porque o modelo padrao precisa ser
baixado. Consulte os logs:

```bash
docker compose logs -f ollama local-llm-server
```

## 5. Validar a instalacao

Liveness da API:

```bash
curl http://localhost:8000/health/live
```

Readiness, incluindo provider e modelo:

```bash
curl http://localhost:8000/health/ready
```

Swagger:

```text
http://localhost:8000/docs
```

Interface web:

```text
http://localhost:8000/
```

Listagem autenticada de modelos:

```bash
curl http://localhost:8000/v1/models \
  -H "X-API-Key: sua-chave-local"
```

No PowerShell, use `curl.exe` para garantir que o executavel curl seja usado:

```powershell
curl.exe http://localhost:8000/v1/models `
  -H "X-API-Key: sua-chave-local"
```

## 6. Testar uma conversa

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-local" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "user", "content": "Responda em uma frase: o que e uma API?"}
    ]
  }'
```

Streaming:

```bash
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-local" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "user", "content": "Explique Docker brevemente."}
    ],
    "stream": true
  }'
```

## 7. Profiles opcionais

Redis para rate limiting distribuido:

```bash
docker compose --profile redis up --build -d
```

Prometheus e Grafana:

```bash
docker compose --profile monitoring up --build -d
```

Jaeger e OpenTelemetry Collector:

```bash
docker compose --profile tracing up --build -d
```

Monitoring e tracing juntos:

```bash
docker compose --profile monitoring --profile tracing up --build -d
```

Interfaces opcionais:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Jaeger: `http://localhost:16686`

## 8. Executar testes fora do Docker

Crie um ambiente Python 3.12:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
python -m pip install -r requirements.txt
```

Execute os quality gates:

```bash
python -m pytest -q
ruff check app tests scripts
mypy app tests scripts --ignore-missing-imports --no-error-summary
```

## 9. Benchmark local

Com a API em execucao:

```bash
python scripts/benchmark.py \
  --path /health/live \
  --requests 100 \
  --concurrency 10 \
  --warmup 5 \
  --sample-memory \
  --output reports/health.json
```

Para chat e streaming, o provider e o modelo precisam estar disponiveis:

```bash
python scripts/benchmark.py \
  --path /v1/chat/completions \
  --model llama3.2:3b \
  --requests 20 \
  --concurrency 2 \
  --stream \
  --api-key sua-chave-local \
  --output reports/chat.json
```

## 10. Exemplos de clientes

Os exemplos ficam em `examples/`:

- Python: `examples/python/client.py`
- Node.js: `examples/node/client.mjs`
- C#: `examples/csharp/Program.cs`

Eles usam `LOCAL_LLM_API_KEY` e `LOCAL_LLM_MODEL`, com fallback para `API_KEY` e
`DEFAULT_MODEL`. Consulte `examples/README.md` para os comandos completos.

## 11. Alterar provider

Ollama, padrao:

```env
PROVIDER_NAME=ollama
OLLAMA_URL=http://ollama:11434
```

LM Studio executando no host:

```env
PROVIDER_NAME=lmstudio
LMSTUDIO_URL=http://host.docker.internal:1234
```

vLLM executando em outro servico local:

```env
PROVIDER_NAME=vllm
VLLM_URL=http://vllm:8000
```

Fallback:

```env
PROVIDER_NAME=ollama
FALLBACK_PROVIDER_NAME=lmstudio
```

Depois de alterar o `.env`, recrie a API:

```bash
docker compose up --build -d local-llm-server
```

## 12. Parar, reiniciar e limpar

Reiniciar sem recriar imagens:

```bash
docker compose restart
```

Parar e remover containers e rede, preservando volumes:

```bash
docker compose down
```

Remover também volumes locais, incluindo modelos baixados:

```bash
docker compose down -v
```

Use `down -v` somente quando quiser baixar os modelos novamente.

## Troubleshooting

### `Invalid API Key`

A chave enviada pelo cliente precisa ser igual a `API_KEY` ou estar dentro de
`ALLOWED_API_KEYS` no `.env`. Depois de alterar o `.env`, recrie o container da
API.

### `Unable to connect to Ollama`

- Com Docker, confirme `OLLAMA_URL=http://ollama:11434`.
- Fora do Docker, use `OLLAMA_URL=http://localhost:11434`.
- Execute `docker compose ps` e verifique se o container `ollama` esta healthy.
- Consulte `docker compose logs ollama`.

### `/health/ready` esta `not_ready`

O Ollama pode estar baixando o modelo. Aguarde e consulte:

```bash
docker compose logs -f ollama
```

### Porta ocupada

Altere a porta publicada no Compose, por exemplo:

```yaml
ports:
  - "8001:8000"
```

Depois acesse `http://localhost:8001`.
