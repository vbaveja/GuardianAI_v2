"""Object detection data contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """Recognized object and its location in the original frame."""

    # Human-readable class label, such as "person" or "squirrel".
    label: str

    # Numeric class identifier produced by the model.
    class_id: int

    # Detection confidence score between 0.0 and 1.0.
    confidence: float

    # Bounding box in original-frame pixel coordinates: (x1, y1, x2, y2).
    box: tuple[int, int, int, int]
