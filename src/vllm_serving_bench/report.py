from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_results(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_markdown(results: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# vLLM Benchmark Report")
    lines.append("")
    lines.append(f"- model: `{results.get('model')}`")
    lines.append(f"- endpoint: `{results.get('endpoint')}`")
    lines.append(f"- stream: `{results.get('stream')}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| experiment | concurrency | input tokens | max tokens | rps | out tok/s | p50 latency | p99 latency | p50 TTFT | p99 TTFT | p50 TPOT | error rate |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for item in results["results"]:
        cfg = item["config"]
        lines.append(
            "| {name} | {c} | {inp} | {out} | {rps} | {tps} | {p50} | {p99} | {ttft50} | {ttft99} | {tpot50} | {err} |".format(
                name=item["experiment"],
                c=cfg["concurrency"],
                inp=cfg["input_tokens"],
                out=cfg["max_tokens"],
                rps=_fmt(item["request_throughput_rps"]),
                tps=_fmt(item["output_throughput_tokens_s"]),
                p50=_fmt(item["latency_p50_s"]),
                p99=_fmt(item["latency_p99_s"]),
                ttft50=_fmt(item["ttft_p50_s"]),
                ttft99=_fmt(item["ttft_p99_s"]),
                tpot50=_fmt(item["tpot_p50_s"]),
                err=_fmt(item["error_rate"]),
            )
        )
    lines.append("")
    lines.append("## Analysis Checklist")
    lines.append("")
    lines.append("- Does throughput scale with concurrency, or does it plateau early?")
    lines.append("- Does P99 latency grow much faster than P50 latency?")
    lines.append("- Does longer input mainly hurt TTFT, indicating prefill pressure?")
    lines.append("- Does longer output mainly hurt TPOT, indicating decode pressure?")
    lines.append("- Is `max-num-batched-tokens` too small for the workload?")
    lines.append("- Is GPU memory high enough to create KV cache pressure?")
    lines.append("")
    return "\n".join(lines)


def write_report(input_path: str | Path, output_path: str | Path) -> None:
    results = load_results(input_path)
    report = render_markdown(results)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")

