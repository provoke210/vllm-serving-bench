# Resume Framing

## Chinese

基于 vLLM 构建 OpenAI-compatible 大模型推理服务性能评测平台，设计异步压测工具统计 TTFT、TPOT、P50/P99 延迟、tokens/s、错误率与并发扩展性；围绕输入长度、输出长度、并发数、batching 参数和显存利用率进行实验，分析 PagedAttention、continuous batching 与 KV Cache 对服务吞吐和尾延迟的影响，并形成可复现实验报告。

## English

Built a vLLM-based OpenAI-compatible LLM serving benchmark platform with an asynchronous load generator to measure TTFT, TPOT, P50/P99 latency, tokens/s, error rate, and concurrency scalability. Evaluated the impact of input length, output length, concurrency, batching parameters, and GPU memory utilization, and analyzed how PagedAttention, continuous batching, and KV cache management affect throughput and tail latency.

## Interview Talking Points

- Why TTFT and TPOT should be separated.
- Why long prompts mainly hurt prefill latency.
- Why long generations mainly stress decode throughput.
- How continuous batching differs from static batching.
- How PagedAttention reduces KV cache fragmentation.
- Why P99 latency matters more than average latency in production serving.

