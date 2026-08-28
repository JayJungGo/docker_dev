# qec/src/qec_sim/cli.py

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .domain import ExperimentConfig
from .evaluation import LogicalErrorEvaluator
from .metadata import (
    PackageRuntimeInfoProvider,
    ReproducibilityMetadataBuilder,
)
from .pymatching_backend import (
    PyMatchingDecoder,
)
from .runner import ExperimentRunner
from .stim_backend import (
    StimCircuitBuilder,
    StimCircuitInspector,
    StimDetectorErrorModelBuilder,
    StimSyndromeSampler,
)
from .storage import (
    FileSystemResultWriter,
    RunNameGenerator,
)


def parse_config() -> ExperimentConfig:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--task",
        default=
            "surface_code:rotated_memory_x",
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
        default=Path(
            "/workspace/data/qec/raw"
        ),
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


def build_runner() -> ExperimentRunner:

    runtime_info = (
        PackageRuntimeInfoProvider()
    )

    metadata_builder = (
        ReproducibilityMetadataBuilder(
            runtime_info
        )
    )

    writer = FileSystemResultWriter(
        RunNameGenerator()
    )

    return ExperimentRunner(
        circuit_builder=
            StimCircuitBuilder(),

        error_model_builder=
            StimDetectorErrorModelBuilder(),

        sampler=
            StimSyndromeSampler(),

        decoder=
            PyMatchingDecoder(),

        evaluator=
            LogicalErrorEvaluator(),

        circuit_inspector=
            StimCircuitInspector(),

        metadata_factory=
            metadata_builder,

        result_writer=
            writer,
    )


def main() -> None:

    config = parse_config()

    runner = build_runner()

    summary = runner.run(
        config
    )

    print(
        json.dumps(
            summary.metadata,
            indent=2,
        )
    )

    print(
        "\nSaved to:",
        summary.output_dir,
    )


if __name__ == "__main__":
    main()
