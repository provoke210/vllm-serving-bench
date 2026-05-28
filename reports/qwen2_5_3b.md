# vLLM Benchmark Report

- model: `/root/autodl-tmp/models/Qwen2.5-3B-Instruct`
- endpoint: `http://127.0.0.1:8000/v1/completions`
- stream: `True`

## Summary

| experiment | concurrency | input tokens | max tokens | rps | out tok/s | p50 latency | p99 latency | p50 TTFT | p99 TTFT | p50 TPOT | error rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| c1_in128_out128 | 1 | 128 | 128 | 0.807 | 82.829 | 1.234 | 1.287 | 0.037 | 0.085 | 0.012 | 0.000 |
| c4_in128_out128 | 4 | 128 | 128 | 2.824 | 291.399 | 1.411 | 1.424 | 0.038 | 0.044 | 0.013 | 0.000 |
| c8_in512_out128 | 8 | 512 | 128 | 5.097 | 522.486 | 1.505 | 1.695 | 0.063 | 0.256 | 0.014 | 0.000 |
| c8_in512_out512 | 8 | 512 | 512 | 1.361 | 557.458 | 5.872 | 5.884 | 0.069 | 0.074 | 0.014 | 0.000 |
| c16_in512_out128 | 16 | 512 | 128 | 9.645 | 988.935 | 1.654 | 1.661 | 0.104 | 0.114 | 0.015 | 0.000 |

## Analysis Checklist

- Does throughput scale with concurrency, or does it plateau early?
- Does P99 latency grow much faster than P50 latency?
- Does longer input mainly hurt TTFT, indicating prefill pressure?
- Does longer output mainly hurt TPOT, indicating decode pressure?
- Is `max-num-batched-tokens` too small for the workload?
- Is GPU memory high enough to create KV cache pressure?
