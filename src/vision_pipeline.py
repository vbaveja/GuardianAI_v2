"""Vision pipeline coordination interface."""

from typing import Any

from src.core.layer import Layer
from src.types.pipeline import PipelineResult


class VisionPipeline:
    """Coordinate camera capture, preprocessing, inference, and detection."""

    def start(self) -> None:
        """Start pipeline resources."""
        # TODO: Start camera and load required perception resources.

    def process(self) -> PipelineResult:
        """Process one frame captured by the pipeline camera.

        Returns:
            Immutable pipeline result.
        """
        # TODO: Capture and process one camera frame.

    def process_frame(self, frame: Any) -> PipelineResult:
        """Process a provided frame.

        Args:
            frame: Frame supplied by tests, still images, or external capture.

        Returns:
            Immutable pipeline result.
        """
        # TODO: Run preprocessing, inference, detection, and layer selection.

    def set_layer(self, layer: Layer) -> None:
        """Set the active educational layer.

        Args:
            layer: Educational layer to expose.
        """
        # TODO: Store and validate the active layer.

    def stop(self) -> None:
        """Stop pipeline resources."""
        # TODO: Release camera and pipeline resources.
