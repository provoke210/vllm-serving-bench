param(
  [string]$Config = "configs/experiments/sweep_small.yaml",
  [string]$Output = "reports/results_small.json",
  [string]$Python = "E:\python\python.exe"
)

$env:PYTHONPATH = "$PWD\src"
$Report = [System.IO.Path]::ChangeExtension($Output, ".md")

& $Python -m vllm_serving_bench.cli run --config $Config --output $Output
& $Python -m vllm_serving_bench.cli report --input $Output --output $Report
