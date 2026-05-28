from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

from .config import BenchConfig, ExperimentConfig
from .datasets import load_prompts, shape_prompt
from .metrics import RequestMetrics, summarize
from .openai_client import RequestSpec, request_completion


console = Console()


async def _run_one_experiment(
    config: BenchConfig,
    experiment: ExperimentConfig,
    prompts: list[str],
) -> dict[str, Any]:
    timeout = httpx.Timeout(config.timeout_seconds)
    limits = httpx.Limits(max_connections=experiment.concurrency * 2)
    semaphore = asyncio.Semaphore(experiment.concurrency)
    metrics: list[RequestMetrics] = []

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        async def one_request(i: int) -> None:
            raw_prompt = prompts[i % len(prompts)]
            user_prompt = shape_prompt(raw_prompt, experiment.input_tokens)
            spec = RequestSpec(
                experiment=experiment.name,
                endpoint=config.endpoint,
                api_key=config.api_key,
                model=config.model,
                system_prompt=config.system_prompt,
                user_prompt=user_prompt,
                max_tokens=experiment.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                stream=config.stream,
            )
            async with semaphore:
                metrics.append(await request_completion(client, spec))

        start = time.perf_counter()
        await asyncio.gather(*(one_request(i) for i in range(experiment.num_requests)))
        wall_time_s = time.perf_counter() - start

    summary = summarize(experiment.name, metrics, wall_time_s)
    summary["config"] = experiment.model_dump()
    summary["requests_detail"] = [m.to_dict() for m in metrics]
    return summary


async def run_benchmark(config: BenchConfig) -> dict[str, Any]:
    prompts = load_prompts(config.prompt_file)
    results: list[dict[str, Any]] = []

    for experiment in config.experiments:
        console.print(f"[bold cyan]Running[/bold cyan] {experiment.name}")
        result = await _run_one_experiment(config, experiment, prompts)
        results.append(result)
        _print_summary(result)

    return {
        "endpoint": config.endpoint,
        "model": config.model,
        "stream": config.stream,
        "results": results,
    }


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _print_summary(result: dict[str, Any]) -> None:
    table = Table(title=result["experiment"])
    table.add_column("metric")
    table.add_column("value", justify="right")
    for key in [
        "successful_requests",
        "failed_requests",
        "request_throughput_rps",
        "output_throughput_tokens_s",
        "latency_p50_s",
        "latency_p99_s",
        "ttft_p50_s",
        "ttft_p99_s",
        "tpot_p50_s",
        "tpot_p99_s",
    ]:
        table.add_row(key, _fmt(result.get(key)))
    console.print(table)


def ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

