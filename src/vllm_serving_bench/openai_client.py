from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .metrics import RequestMetrics


@dataclass
class RequestSpec:
    experiment: str
    endpoint: str
    api_key: str
    model: str
    system_prompt: str | None
    user_prompt: str
    max_tokens: int
    temperature: float
    top_p: float
    stream: bool


def _payload(spec: RequestSpec) -> dict[str, Any]:
    if spec.endpoint.rstrip("/").endswith("/v1/completions"):
        prompt = spec.user_prompt
        if spec.system_prompt:
            prompt = f"{spec.system_prompt}\n\n{prompt}"
        return {
            "model": spec.model,
            "prompt": prompt,
            "max_tokens": spec.max_tokens,
            "temperature": spec.temperature,
            "top_p": spec.top_p,
            "stream": spec.stream,
        }

    messages: list[dict[str, str]] = []
    if spec.system_prompt:
        messages.append({"role": "system", "content": spec.system_prompt})
    messages.append({"role": "user", "content": spec.user_prompt})
    return {
        "model": spec.model,
        "messages": messages,
        "max_tokens": spec.max_tokens,
        "temperature": spec.temperature,
        "top_p": spec.top_p,
        "stream": spec.stream,
    }


def _estimate_tokens(text: str) -> int:
    # Good enough for throughput trend analysis when the endpoint omits usage.
    if not text:
        return 0
    return max(1, len(text.split()))


async def request_completion(client: httpx.AsyncClient, spec: RequestSpec) -> RequestMetrics:
    headers = {"Authorization": f"Bearer {spec.api_key}"}
    start = time.perf_counter()
    ttft: float | None = None
    output_text: list[str] = []

    try:
        if spec.stream:
            async with client.stream("POST", spec.endpoint, headers=headers, json=_payload(spec)) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break
                    if ttft is None:
                        ttft = time.perf_counter() - start
                    chunk = json.loads(data)
                    choice = chunk["choices"][0]
                    if "delta" in choice:
                        output_text.append(choice["delta"].get("content") or "")
                    else:
                        output_text.append(choice.get("text") or "")
            latency = time.perf_counter() - start
            return RequestMetrics(
                experiment=spec.experiment,
                ok=True,
                latency_s=latency,
                ttft_s=ttft,
                output_tokens=_estimate_tokens("".join(output_text)),
            )

        response = await client.post(spec.endpoint, headers=headers, json=_payload(spec))
        response.raise_for_status()
        latency = time.perf_counter() - start
        body = response.json()
        choice = body["choices"][0]
        if "message" in choice:
            content = choice["message"].get("content") or ""
        else:
            content = choice.get("text") or ""
        usage_tokens = body.get("usage", {}).get("completion_tokens")
        return RequestMetrics(
            experiment=spec.experiment,
            ok=True,
            latency_s=latency,
            ttft_s=None,
            output_tokens=int(usage_tokens) if usage_tokens is not None else _estimate_tokens(content),
        )
    except Exception as exc:  # noqa: BLE001 - benchmark records failures instead of crashing.
        latency = time.perf_counter() - start
        return RequestMetrics(
            experiment=spec.experiment,
            ok=False,
            latency_s=latency,
            ttft_s=ttft,
            output_tokens=0,
            error=repr(exc),
        )
