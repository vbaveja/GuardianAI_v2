"""Detector interface for decoding raw model predictions."""

from pathlib import Path
from typing import Any

from src.types.detection import Detection
from src.types.preprocessing import PreprocessingResult


class Detector:
    """Convert raw inference output into object detections."""

    def load_labels(self, path: str | Path) -> None:
        """Load class labels.

        Args:
            path: Path to a label file.
        """
        # TODO: Load labels from the provided path.

    def detect(self, raw_output: Any, metadata: PreprocessingResult) -> list[Detection]:
        """Decode raw model output into detections.

        Args:
            raw_output: Raw output returned by the inference engine.
            metadata: Preprocessing metadata for coordinate recovery.

        Returns:
            Detected objects in original frame coordinates.
        """
        # TODO: Apply confidence filtering, NMS, and coordinate recovery.
