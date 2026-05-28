from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .config import load_config
from .report import write_report
from .runner import ensure_parent, run_benchmark


def run_command(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    result = asyncio.run(run_benchmark(config))
    ensure_parent(args.output)
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def report_command(args: argparse.Namespace) -> None:
    write_report(args.input, args.output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark OpenAI-compatible vLLM endpoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run benchmark from a YAML config.")
    run_parser.add_argument("--config", required=True)
    run_parser.add_argument("--output", required=True)
    run_parser.set_defaults(func=run_command)

    report_parser = subparsers.add_parser("report", help="Render a markdown report from JSON results.")
    report_parser.add_argument("--input", required=True)
    report_parser.add_argument("--output", required=True)
    report_parser.set_defaults(func=report_command)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

