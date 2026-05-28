from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from statistics import mean
from typing import Any


@dataclass
class RequestMetrics:
    experiment: str
    ok: bool
    latency_s: float
    ttft_s: float | None
    output_tokens: int
    error: str | None = None

    @property
    def tpot_s(self) -> float | None:
        if self.ttft_s is None or self.output_tokens <= 1:
            return None
        return max(self.latency_s - self.ttft_s, 0.0) / (self.output_tokens - 1)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tpot_s"] = self.tpot_s
        return data


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def summarize(experiment: str, metrics: list[RequestMetrics], wall_time_s: float) -> dict[str, Any]:
    ok = [m for m in metrics if m.ok]
    failed = [m for m in metrics if not m.ok]
    latencies = [m.latency_s for m in ok]
    ttfts = [m.ttft_s for m in ok if m.ttft_s is not None]
    tpots = [m.tpot_s for m in ok if m.tpot_s is not None]
    output_tokens = sum(m.output_tokens for m in ok)

    return {
        "experiment": experiment,
        "requests": len(metrics),
        "successful_requests": len(ok),
        "failed_requests": len(failed),
        "error_rate": len(failed) / len(metrics) if metrics else 0.0,
        "wall_time_s": wall_time_s,
        "request_throughput_rps": len(ok) / wall_time_s if wall_time_s > 0 else None,
        "output_throughput_tokens_s": output_tokens / wall_time_s if wall_time_s > 0 else None,
        "latency_avg_s": mean(latencies) if latencies else None,
        "latency_p50_s": percentile(latencies, 0.50),
        "latency_p90_s": percentile(latencies, 0.90),
        "latency_p95_s": percentile(latencies, 0.95),
        "latency_p99_s": percentile(latencies, 0.99),
        "ttft_avg_s": mean(ttfts) if ttfts else None,
        "ttft_p50_s": percentile(ttfts, 0.50),
        "ttft_p99_s": percentile(ttfts, 0.99),
        "tpot_avg_s": mean(tpots) if tpots else None,
        "tpot_p50_s": percentile(tpots, 0.50),
        "tpot_p99_s": percentile(tpots, 0.99),
        "output_tokens": output_tokens,
    }

