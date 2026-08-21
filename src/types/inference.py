"""Inference result data contract."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InferenceResult:
    """Raw model output and timing from an inference pass."""

    # Raw output produced by the inference runtime.
    raw_output: Any

    # Inference duration in milliseconds.
    inference_ms: float
