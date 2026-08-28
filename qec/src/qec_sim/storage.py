# qec/src/qec_sim/storage.py

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .domain import (
    ExperimentConfig,
    ExperimentOutput,
)


class RunNameGenerator:

    def create(
        self,
        config: ExperimentConfig,
    ) -> str:

        task = config.task.replace(
            ":",
            "_"
        )

        return (
            f"{task}"
            f"_d{config.distance}"
            f"_r{config.effective_rounds}"
            f"_p{config.depolarizing_p:g}"
            f"_pm{config.measurement_p:g}"
            f"_seed{config.seed}"
        )


class FileSystemResultWriter:

    def __init__(
        self,
        run_name_generator: RunNameGenerator,
    ):
        self._run_name_generator = (
            run_name_generator
        )

    def write(
        self,
        output: ExperimentOutput,
    ) -> Path:

        run_name = (
            self._run_name_generator.create(
                output.config
            )
        )

        directory = (
            output.config.output_dir
            / run_name
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._write_arrays(
            directory,
            output,
        )

        self._write_circuit(
            directory,
            output,
        )

        self._write_coordinates(
            directory,
            output,
        )

        self._write_metadata(
            directory,
            output,
        )

        return directory

    @staticmethod
    def _write_arrays(
        directory: Path,
        output: ExperimentOutput,
    ) -> None:

        np.save(
            directory / "detection_events.npy",
            output.batch.detections,
        )

        np.save(
            directory / "observables.npy",
            output.batch.observables,
        )

        np.save(
            directory / "mwpm_predictions.npy",
            output.predictions,
        )

    @staticmethod
    def _write_circuit(
        directory: Path,
        output: ExperimentOutput,
    ) -> None:

        (
            directory
            / "circuit.stim"
        ).write_text(
            str(output.circuit),
            encoding="utf-8",
        )

        (
            directory
            / "detector_error_model.dem"
        ).write_text(
            str(output.detector_error_model),
            encoding="utf-8",
        )

    @staticmethod
    def _write_coordinates(
        directory: Path,
        output: ExperimentOutput,
    ) -> None:

        coordinates = {
            str(key): list(value)
            for key, value
            in output.detector_coordinates.items()
        }

        with (
            directory
            / "detector_coordinates.json"
        ).open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                coordinates,
                file,
                indent=2,
            )

    @staticmethod
    def _write_metadata(
        directory: Path,
        output: ExperimentOutput,
    ) -> None:

        with (
            directory
            / "metadata.json"
        ).open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                output.metadata,
                file,
                indent=2,
            )
