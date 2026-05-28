param(
  [string]$Model = "Qwen/Qwen2.5-0.5B-Instruct",
  [int]$Port = 8000,
  [string]$DType = "auto",
  [double]$GpuMemoryUtilization = 0.90,
  [int]$MaxNumSeqs = 32,
  [int]$MaxNumBatchedTokens = 4096
)

vllm serve $Model `
  --host 0.0.0.0 `
  --port $Port `
  --dtype $DType `
  --gpu-memory-utilization $GpuMemoryUtilization `
  --max-num-seqs $MaxNumSeqs `
  --max-num-batched-tokens $MaxNumBatchedTokens
