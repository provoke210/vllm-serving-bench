# vLLM Serving Bench

一个面向 AI Infra / LLM Serving 方向的 vLLM 推理服务压测与分析项目。

这个项目的目标不是简单启动 vLLM，而是系统评估 OpenAI-compatible LLM serving 在不同并发、输入长度、输出长度和服务参数下的性能表现，并输出 benchmark report。

## What It Measures

- TTFT: time to first token
- TPOT: time per output token
- end-to-end latency
- P50 / P90 / P95 / P99 latency
- tokens/s
- request throughput
- error rate
- concurrency scaling behavior

## Project Structure

```text
vllm-serving-bench/
  configs/
    experiments/sweep_small.yaml
    models/qwen2_5_1_5b.yaml
  prompts/sample_prompts.jsonl
  reports/benchmark_report_template.md
  scripts/
    start_vllm.ps1
    run_bench.ps1
  src/vllm_serving_bench/
    cli.py
    config.py
    metrics.py
    openai_client.py
    report.py
    runner.py
```

## Quick Start

### 1. Install

vLLM is best run on Linux with NVIDIA GPU. On Windows, use WSL2 + CUDA, a Linux server, or a cloud GPU machine.

```bash
pip install -r requirements.txt
pip install vllm
```

### 2. Start vLLM

Example:

```bash
vllm serve Qwen/Qwen2.5-0.5B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype auto \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 32 \
  --max-num-batched-tokens 4096
```

PowerShell helper:

```powershell
.\scripts\start_vllm.ps1 -Model Qwen/Qwen2.5-0.5B-Instruct
```

### 3. Run Benchmark

```bash
python -m vllm_serving_bench.cli run \
  --config configs/experiments/sweep_small.yaml \
  --output reports/results_small.json
```

PowerShell helper:

```powershell
$env:PYTHONPATH="E:\大模型项目\vllm-serving-bench\src"
.\scripts\run_bench.ps1
```

Low-VRAM first run:

```powershell
.\scripts\run_bench.ps1 -Config configs/experiments/low_vram_qwen2_5_0_5b.yaml -Output reports/low_vram_qwen2_5_0_5b.json
```

Qwen2.5-3B run:

```bash
python -m vllm_serving_bench.cli run \
  --config configs/experiments/qwen2_5_3b.yaml \
  --output reports/qwen2_5_3b.json
python -m vllm_serving_bench.cli report \
  --input reports/qwen2_5_3b.json \
  --output reports/qwen2_5_3b.md
```

### 4. Generate Markdown Report

```bash
python -m vllm_serving_bench.cli report \
  --input reports/results_small.json \
  --output reports/results_small.md
```

## Suggested Experiments

Start with a small model and a small sweep:

- model: `Qwen/Qwen2.5-0.5B-Instruct`
- concurrency: `1, 4, 8, 16`
- input tokens: `128, 512, 2048`
- output tokens: `128, 512`

Then expand:

- compare 1.5B vs 3B vs 7B
- compare FP16/BF16 vs AWQ/GPTQ
- tune `max-num-batched-tokens`
- tune `max-num-seqs`
- test long context impact on TTFT
- test streaming vs non-streaming


## Notes

- This repo does not require vLLM to run unit-level parsing checks.
- Real benchmark requires a running OpenAI-compatible endpoint.
- Token counts are estimated from response usage when available, otherwise approximated from streamed text.
- On Windows, run vLLM through WSL2 or a Linux GPU server. See `docs/windows_wsl_run.md`.
