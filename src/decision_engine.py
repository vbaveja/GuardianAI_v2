"""Decision engine for converting detections into decisions."""

from src.types.decision import Decision
from src.types.detection import Detection


class DecisionEngine:
    """Evaluate detections and produce hardware-independent decisions."""

    def evaluate(self, detections: list[Detection] | tuple[Detection, ...]) -> Decision | list[Decision]:
        """Evaluate detections.

        Args:
            detections: Objects recognized by the detector.

        Returns:
            Decision or decisions for the action engine.
        """
        # TODO: Add application-specific reasoning rules.
