import time

from prometheus_client import Counter, Histogram


REQUESTS_TOTAL = Counter(
    "local_llm_requests_total",
    "Total de requisicoes HTTP processadas.",
    ["method", "path", "status"],
)
REQUEST_DURATION_SECONDS = Histogram(
    "local_llm_request_duration_seconds",
    "Duracao das requisicoes HTTP em segundos.",
    ["method", "path"],
)
INFERENCE_REQUESTS_TOTAL = Counter(
    "local_llm_inference_requests_total",
    "Total de requisicoes de inferencia.",
    ["path", "status"],
)
TOKENS_TOTAL = Counter(
    "local_llm_tokens_total",
    "Total de tokens reportados pelo provider.",
    ["model", "type"],
)


def observe_request(method: str, path: str, status_code: int, started_at: float) -> None:
    status = str(status_code)
    duration = time.perf_counter() - started_at
    REQUESTS_TOTAL.labels(method=method, path=path, status=status).inc()
    REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)

    if path == "/ask" or path.startswith("/v1/"):
        INFERENCE_REQUESTS_TOTAL.labels(path=path, status=status).inc()


def observe_tokens(model: str, prompt_tokens: int, completion_tokens: int) -> None:
    TOKENS_TOTAL.labels(model=model, type="prompt").inc(prompt_tokens)
    TOKENS_TOTAL.labels(model=model, type="completion").inc(completion_tokens)
