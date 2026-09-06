import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class RequestResult:
    duration_ms: float
    status_code: int | None
    error: str | None = None
    time_to_first_byte_ms: float | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark a running Local LLM Server instance.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--path", default="/health/live")
    parser.add_argument("--model", default=os.getenv("DEFAULT_MODEL", "llama3.2:3b"))
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--api-key", default=os.getenv("API_KEY"))
    parser.add_argument("--stream", action="store_true")
    return parser.parse_args()


async def request_once(
    client: httpx.AsyncClient,
    path: str,
    model: str,
    stream: bool,
) -> RequestResult:
    payload: dict[str, Any] | None = None
    if path == "/v1/chat/completions":
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with one short word."}],
            "stream": stream,
            "max_tokens": 16,
        }

    started = time.perf_counter()
    first_byte_at: float | None = None
    try:
        if stream:
            async with client.stream("POST", path, json=payload) as response:
                response.raise_for_status()
                async for _ in response.aiter_bytes():
                    if first_byte_at is None:
                        first_byte_at = time.perf_counter()
        else:
            response = await client.request("POST" if payload else "GET", path, json=payload)
            response.raise_for_status()
    except (httpx.HTTPError, OSError) as exc:
        return RequestResult(
            duration_ms=(time.perf_counter() - started) * 1000,
            status_code=getattr(locals().get("response"), "status_code", None),
            error=str(exc),
        )

    finished = time.perf_counter()
    return RequestResult(
        duration_ms=(finished - started) * 1000,
        status_code=response.status_code,
        time_to_first_byte_ms=((first_byte_at - started) * 1000 if first_byte_at is not None else None),
    )


async def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    if args.requests <= 0 or args.concurrency <= 0 or args.warmup < 0:
        raise ValueError("requests and concurrency must be positive; warmup cannot be negative")

    headers = {"Authorization": f"Bearer {args.api_key}"} if args.api_key else {}
    limits = httpx.Limits(max_connections=args.concurrency, max_keepalive_connections=args.concurrency)
    timeout = httpx.Timeout(args.timeout)
    async with httpx.AsyncClient(
        base_url=args.base_url.rstrip("/"),
        headers=headers,
        timeout=timeout,
        limits=limits,
    ) as client:
        for _ in range(args.warmup):
            result = await request_once(client, args.path, args.model, args.stream)
            if result.error:
                raise RuntimeError(f"Warmup failed: {result.error}")

        queue: asyncio.Queue[int] = asyncio.Queue()
        for index in range(args.requests):
            queue.put_nowait(index)
        results: list[RequestResult] = []
        results_lock = asyncio.Lock()

        async def worker() -> None:
            while not queue.empty():
                await queue.get()
                try:
                    result = await request_once(client, args.path, args.model, args.stream)
                    async with results_lock:
                        results.append(result)
                finally:
                    queue.task_done()

        started = time.perf_counter()
        await asyncio.gather(*(worker() for _ in range(args.concurrency)))
        elapsed_seconds = time.perf_counter() - started

    successful = [result for result in results if result.error is None]
    durations = sorted(result.duration_ms for result in successful)
    report: dict[str, Any] = {
        "base_url": args.base_url,
        "path": args.path,
        "requests": args.requests,
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "concurrency": args.concurrency,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "throughput_requests_per_second": round(len(successful) / elapsed_seconds, 3) if elapsed_seconds else 0,
        "latency_ms": latency_summary(durations),
    }
    if args.stream:
        first_bytes = sorted(
            result.time_to_first_byte_ms for result in successful if result.time_to_first_byte_ms is not None
        )
        report["time_to_first_byte_ms"] = latency_summary(first_bytes)
    failures = [result.error for result in results if result.error]
    if failures:
        report["errors"] = failures[:5]
    return report


def latency_summary(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "median": None, "p95": None, "p99": None, "max": None}

    def percentile(percent: float) -> float:
        index = min(len(values) - 1, round((len(values) - 1) * percent / 100))
        return round(values[index], 3)

    return {
        "min": round(values[0], 3),
        "median": round(statistics.median(values), 3),
        "p95": percentile(95),
        "p99": percentile(99),
        "max": round(values[-1], 3),
    }


def main() -> int:
    args = parse_args()
    try:
        report = asyncio.run(run_benchmark(args))
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
