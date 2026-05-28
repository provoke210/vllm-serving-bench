# vLLM Benchmark Report Template

## Experiment Setup

- GPU:
- CPU:
- RAM:
- CUDA:
- vLLM:
- model:
- dtype:
- quantization:
- `max-num-seqs`:
- `max-num-batched-tokens`:
- `gpu-memory-utilization`:

## Key Results

| workload | concurrency | input tokens | output tokens | tokens/s | P50 TTFT | P99 TTFT | P50 latency | P99 latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| short QA | 1 | 128 | 128 | | | | | |
| short QA | 8 | 128 | 128 | | | | | |
| long input | 8 | 2048 | 128 | | | | | |
| long output | 8 | 512 | 512 | | | | | |

## Observations

- Throughput:
- TTFT:
- TPOT:
- P99 latency:
- Failure rate:

## Mechanism Analysis

- Prefill is mainly affected by input length because the model computes attention over the prompt.
- Decode is mainly affected by generated length and batch scheduling.
- KV cache memory grows with batch size, sequence length, number of layers, hidden size, and dtype.
- Continuous batching improves utilization by admitting new requests while existing requests decode.
- PagedAttention reduces KV cache fragmentation compared with naive contiguous allocation.

## Optimization Ideas

- Tune `max-num-batched-tokens`.
- Tune `max-num-seqs`.
- Use quantization when memory pressure dominates.
- Reduce max output length for latency-sensitive endpoints.
- Separate long-context traffic from short interactive traffic.

