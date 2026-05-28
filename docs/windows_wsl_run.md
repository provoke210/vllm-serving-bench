# Run vLLM on Windows with WSL2

vLLM does not provide a native Windows wheel in this environment. Use WSL2 + Ubuntu or a Linux GPU server.

## 1. Install WSL2 Ubuntu

Run PowerShell as administrator:

```powershell
wsl --install -d Ubuntu
```

Reboot if Windows asks for it. Then open Ubuntu.

## 2. Check GPU in WSL

Inside Ubuntu:

```bash
nvidia-smi
```

You should see the RTX 3070 Laptop GPU.

## 3. Enter the Project

Windows drive `E:` is mounted under `/mnt/e` in WSL:

```bash
cd /mnt/e/大模型项目/vllm-serving-bench
```

## 4. Create Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install vllm
```

## 5. Start vLLM with Qwen2.5-0.5B

For an 8GB GPU, start conservatively:

```bash
vllm serve Qwen/Qwen2.5-0.5B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype float16 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.80 \
  --max-num-seqs 16 \
  --max-num-batched-tokens 2048
```

## 6. Run Low-VRAM Benchmark

Open a second Ubuntu terminal:

```bash
cd /mnt/e/大模型项目/vllm-serving-bench
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m vllm_serving_bench.cli run \
  --config configs/experiments/low_vram_qwen2_5_0_5b.yaml \
  --output reports/low_vram_qwen2_5_0_5b.json
python -m vllm_serving_bench.cli report \
  --input reports/low_vram_qwen2_5_0_5b.json \
  --output reports/low_vram_qwen2_5_0_5b.md
```

## Expected Hardware Fit

Your RTX 3070 Laptop has 8GB VRAM. Qwen2.5-0.5B should fit with the conservative settings above.

If CUDA OOM appears:

- reduce `--max-model-len` to `2048`
- reduce `--max-num-seqs` to `8`
- reduce `--max-num-batched-tokens` to `1024`
- close GPU-heavy Windows applications

