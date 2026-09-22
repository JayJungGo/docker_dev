# qec/src/qec_sim/cli.py

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .domain import ExperimentConfig
from .factory import build_runner


def parse_config() -> ExperimentConfig:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--task",
        default="surface_code:rotated_memory_x",
    )

    parser.add_argument(
        "--distance",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--rounds",
        type=int,
    )

    parser.add_argument(
        "--p",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--pm",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--shots",
        type=int,
        default=10_000,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20260819,
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=Path("/workspace/data/qec/raw"),
    )

    args = parser.parse_args()

    return ExperimentConfig(
        task=args.task,
        distance=args.distance,
        rounds=args.rounds,
        depolarizing_p=args.p,
        measurement_p=args.pm,
        shots=args.shots,
        seed=args.seed,
        output_dir=args.out,
    )


def main() -> None:

    config = parse_config()
    runner = build_runner()
    summary = runner.run(config)

    print(json.dumps(summary.metadata, indent=2))
    print("\nSaved to:", summary.output_dir)


if __name__ == "__main__":
    main()
