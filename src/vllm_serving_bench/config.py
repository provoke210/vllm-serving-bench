from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ExperimentConfig(BaseModel):
    name: str
    concurrency: int = Field(ge=1)
    num_requests: int = Field(ge=1)
    input_tokens: int = Field(ge=1)
    max_tokens: int = Field(ge=1)


class BenchConfig(BaseModel):
    endpoint: str
    model: str
    api_key: str = "EMPTY"
    timeout_seconds: float = 180
    stream: bool = True
    prompt_file: str
    system_prompt: str | None = None
    temperature: float = 0.0
    top_p: float = 1.0
    experiments: list[ExperimentConfig]


def load_config(path: str | Path) -> BenchConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return BenchConfig.model_validate(data)

