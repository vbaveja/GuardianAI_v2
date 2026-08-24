"""Lightweight orchestration layer for GuardianAI applications.

Guardian Runtime sits above the existing applications. It chooses which
validated app to launch, but it does not perform inference, detection, GPIO, or
rendering work itself.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD


class RuntimeMode(Enum):
    """Supported GuardianAI runtime modes."""

    LEARNING = "learning"
    RUNTIME = "runtime"


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuration for selecting GuardianAI runtime modules."""

    dashboard: bool = False
    console: bool = False
    object_watch: bool = False
    camera: bool = False
    target_object: str = "person"
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    nms_threshold: float = DEFAULT_NMS_THRESHOLD
    image_path: Path = Path("images/preprocessing_example_original.png")
    model_path: Path = Path("models/object_detector.onnx")
    label_path: Path = Path("labels/coco.txt")
    interval_seconds: float = 1.0


class GuardianRuntime:
    """Coordinate existing GuardianAI applications from one runtime layer."""

    def __init__(self, config: RuntimeConfig) -> None:
        """Create a runtime coordinator.

        Args:
            config: Runtime module selection and shared application settings.
        """
        self._config = config

    @classmethod
    def learning_mode(cls, camera: bool = False) -> "GuardianRuntime":
        """Create a runtime configured for educational visibility.

        Learning Mode enables the Perception Dashboard and Guardian Console.
        Because the runtime is intentionally single-threaded, modules are
        launched one at a time in configuration order.
        """
        return cls(
            RuntimeConfig(
                dashboard=True,
                console=True,
                object_watch=False,
                camera=camera,
            )
        )

    @classmethod
    def runtime_mode(
        cls,
        target_object: str = "person",
        camera: bool = True,
    ) -> "GuardianRuntime":
        """Create a runtime configured for unattended object watching.

        Runtime Mode enables Object Watch. GPIO remains a documented future
        placeholder and is not implemented here.
        """
        return cls(
            RuntimeConfig(
                dashboard=False,
                console=False,
                object_watch=True,
                camera=camera,
                target_object=target_object,
            )
        )

    def run(self) -> None:
        """Launch enabled modules using existing application entry points."""
        if self._config.dashboard:
            self._run_dashboard()

        if self._config.console:
            self._run_console()

        if self._config.object_watch:
            self._run_object_watch()

    def _run_dashboard(self) -> None:
        """Launch the existing Perception Dashboard application."""
        from apps.perception_dashboard import run as run_dashboard

        run_dashboard(
            image_path=self._config.image_path,
            model_path=self._config.model_path,
            label_path=self._config.label_path,
            confidence_threshold=self._config.confidence_threshold,
            nms_threshold=self._config.nms_threshold,
            use_pi_camera=self._config.camera,
        )

    def _run_console(self) -> None:
        """Launch the existing Guardian Console application."""
        from apps.guardian_console import run as run_console

        run_console(
            use_pi_camera=self._config.camera,
            image_path=self._config.image_path,
            model_path=self._config.model_path,
            label_path=self._config.label_path,
            target_label=self._config.target_object,
            confidence_threshold=self._config.confidence_threshold,
            nms_threshold=self._config.nms_threshold,
            interval_seconds=self._config.interval_seconds,
        )

    def _run_object_watch(self) -> None:
        """Launch the existing Object Watch application."""
        from apps.object_watch import run as run_object_watch

        run_object_watch(
            use_pi_camera=self._config.camera,
            image_path=self._config.image_path,
            model_path=self._config.model_path,
            label_path=self._config.label_path,
            target_label=self._config.target_object,
            confidence_threshold=self._config.confidence_threshold,
            nms_threshold=self._config.nms_threshold,
            interval_seconds=self._config.interval_seconds,
        )
