import argparse

import httpx
import pytest

from scripts.benchmark import latency_summary, request_once, run_benchmark, write_report


def benchmark_args(**overrides):
    values = {
        "base_url": "http://test",
        "path": "/health/live",
        "model": "test-model",
        "requests": 3,
        "concurrency": 10,
        "warmup": 1,
        "timeout": 5.0,
        "api_key": None,
        "stream": False,
        "output": None,
        "sample_memory": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


@pytest.mark.asyncio
async def test_benchmark_handles_more_workers_than_requests_and_excludes_warmup():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"status": "alive"})

    report = await run_benchmark(benchmark_args(), httpx.MockTransport(handler))

    assert calls == 4
    assert report["requests"] == 3
    assert report["successful"] == 3
    assert report["failed"] == 0
    assert report["completed_requests_per_second"] > 0
    assert report["successful_requests_per_second"] > 0


@pytest.mark.asyncio
async def test_benchmark_reports_failures_and_memory_sample():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"memory_used_mb": 42.5})
        return httpx.Response(503, json={"error": "unavailable"})

    report = await run_benchmark(
        benchmark_args(requests=2, concurrency=1, warmup=0, sample_memory=True),
        httpx.MockTransport(handler),
    )

    assert report["successful"] == 0
    assert report["failed"] == 2
    assert report["memory_used_mb"] == 42.5
    assert len(report["errors"]) == 2


@pytest.mark.asyncio
async def test_streaming_benchmark_reports_time_to_first_byte():
    def handler(_request: httpx.Request) -> httpx.Response:
        body = 'data: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n'
        return httpx.Response(200, content=body.encode(), headers={"content-type": "text/event-stream"})

    report = await run_benchmark(
        benchmark_args(path="/v1/chat/completions", stream=True, requests=1, concurrency=1, warmup=0),
        httpx.MockTransport(handler),
    )

    assert report["successful"] == 1
    assert report["time_to_first_byte_ms"]["median"] is not None


@pytest.mark.asyncio
async def test_streaming_is_rejected_for_non_chat_paths():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200))) as client:
        result = await request_once(client, "/health/live", "test-model", True)

    assert result.error == "--stream is only supported with /v1/chat/completions"


def test_latency_summary_calculates_percentiles():
    summary = latency_summary([1, 2, 3, 4, 5])

    assert summary == {"min": 1, "median": 3, "p95": 5, "p99": 5, "max": 5}


def test_write_report_persists_json(tmp_path):
    output_path = tmp_path / "benchmark.json"

    write_report({"successful": 3}, str(output_path))

    assert '"successful": 3' in output_path.read_text(encoding="utf-8")
