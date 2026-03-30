from __future__ import annotations

import argparse

from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def cmd_doctor(config_path: str) -> int:
    config = load_config(config_path)
    print("Jarvis Operator doctor check")
    print(f"Provider: {config.provider.type}")
    print(f"State dir: {config.runtime.state_dir}")
    return 0


def cmd_run(task: str, config_path: str) -> int:
    config = load_config(config_path)
    orchestrator = Orchestrator.from_config(config)
    result = orchestrator.run_task(task)
    print(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jarvis-operator")
    parser.add_argument("--config", default="config.example.yaml")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor")

    run_parser = sub.add_parser("run")
    run_parser.add_argument("task")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "doctor":
        return cmd_doctor(args.config)

    if args.command == "run":
        return cmd_run(args.task, args.config)

    return 1
