"""Decision data contract."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class Decision:
    """Hardware-independent decision produced from detections."""

    # Stable action name, such as "none", "alert", or "activate_led".
    action: str

    # Human-readable explanation of why the decision was produced.
    reason: str

    # Optional label or object target associated with the decision.
    target: str | None = None

    # Optional confidence associated with the decision.
    confidence: float | None = None

    # Optional application-specific metadata.
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
