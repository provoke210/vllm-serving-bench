from __future__ import annotations

import json
from pathlib import Path


def load_prompts(path: str | Path) -> list[str]:
    prompt_path = Path(path)
    prompts: list[str] = []
    with prompt_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            prompts.append(str(item["prompt"]))
    if not prompts:
        raise ValueError(f"No prompts found in {prompt_path}")
    return prompts


def shape_prompt(prompt: str, target_tokens: int) -> str:
    # A deterministic token-ish expander. Real tokenization is model-specific;
    # this keeps sweeps comparable without requiring tokenizer downloads.
    words = prompt.split()
    if not words:
        words = ["benchmark"]
    repeated: list[str] = []
    while len(repeated) < target_tokens:
        repeated.extend(words)
    return " ".join(repeated[:target_tokens])

