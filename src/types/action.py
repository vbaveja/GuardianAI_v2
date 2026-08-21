"""Action execution result data contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionResult:
    """Result produced after executing one or more decisions."""

    # Whether the requested action or actions completed successfully.
    success: bool

    # Human-readable execution summary.
    message: str

    # Stable action names executed by the action engine.
    executed_actions: tuple[str, ...]
