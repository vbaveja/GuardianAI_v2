"""Display interface for rendering GuardianAI learning layers."""

from typing import Any

from src.types.pipeline import PipelineResult


class Display:
    """Render and show educational pipeline results."""

    def render(self, result: PipelineResult) -> Any:
        """Render a pipeline result.

        Args:
            result: Immutable output from the vision pipeline.

        Returns:
            Display-ready frame.
        """
        # TODO: Render the selected educational layer.

    def show(self, result: PipelineResult) -> None:
        """Show a pipeline result."""
        # TODO: Display the rendered frame.

    def close(self) -> None:
        """Close display resources."""
        # TODO: Release display resources.
