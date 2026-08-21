"""Preprocessing result data contract."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PreprocessingResult:
    """Model-ready tensor and metadata for coordinate recovery."""

    # Model-ready input tensor.
    tensor: Any

    # Exact image representation provided to the model.
    model_image: Any

    # Original frame shape as (height, width).
    original_shape: tuple[int, int]

    # Resize scale applied before letterboxing.
    scale: float

    # Horizontal padding applied during letterboxing.
    pad_x: int

    # Vertical padding applied during letterboxing.
    pad_y: int
