"""Vision pipeline result data contract."""

from dataclasses import dataclass
from typing import Any

from src.core.layer import Layer
from src.types.detection import Detection
from src.types.inference import InferenceResult
from src.types.preprocessing import PreprocessingResult


@dataclass(frozen=True)
class PipelineResult:
    """Immutable output from a GuardianAI pipeline pass."""

    # Original frame for the current pipeline pass.
    frame: Any

    # Active educational layer.
    layer: Layer

    # Display-ready frame for the active layer.
    display_frame: Any

    # Detections decoded in original-frame coordinates.
    detections: tuple[Detection, ...]

    # Inference result, when the active pass includes model execution.
    inference: InferenceResult | None = None

    # Preprocessing result, when the active pass includes preprocessing.
    preprocessing: PreprocessingResult | None = None
