"""Raw prediction hypothesis data contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Prediction:
    """Ranked hypothesis decoded from one raw neural network prediction."""

    # Zero-based index of the raw prediction in the model output.
    index: int

    # Numeric class identifier with the highest class confidence.
    class_id: int

    # Human-readable label for the best class.
    label: str

    # Highest class confidence score for this prediction.
    confidence: float

    # Predicted box center x-coordinate in model-input coordinates.
    center_x: float

    # Predicted box center y-coordinate in model-input coordinates.
    center_y: float

    # Predicted box width in model-input coordinates.
    width: float

    # Predicted box height in model-input coordinates.
    height: float
