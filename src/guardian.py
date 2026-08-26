"""Application-facing facade for the GuardianAI perception platform.

Guardian composes the existing validated modules into a small API for
applications. It does not replace or refactor the perception pipeline.
"""

from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from apps.object_watch import (  # noqa: E402
    DEFAULT_IMAGE_PATH,
    DEFAULT_LABEL_PATH,
    DEFAULT_MODEL_PATH,
    WatchEvent,
    WatchState,
    best_target_detection,
    create_camera,
    update_state,
)
from src.camera import Camera
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD
from src.detector import Detector
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor
from src.types.detection import Detection
from src.types.prediction import Prediction


@dataclass(frozen=True)
class GuardianFrame:
    """One fully processed GuardianAI frame for application code."""

    detections: tuple[Detection, ...]
    predictions: tuple[Prediction, ...]
    image: Any
    model_image: Any
    inference_ms: float
    _current_labels: frozenset[str]
    _just_detected_labels: frozenset[str]
    _just_disappeared_labels: frozenset[str]

    def sees(self, label: str) -> bool:
        """Return True when the label is visible in this processed frame."""
        return label.lower() in self._current_labels

    def just_detected(self, label: str) -> bool:
        """Return True only on the frame where the label first appeared."""
        return label.lower() in self._just_detected_labels

    def just_disappeared(self, label: str) -> bool:
        """Return True only on the frame where the label disappeared."""
        return label.lower() in self._just_disappeared_labels


class Guardian:
    """Small application facade over the GuardianAI perception pipeline."""

    def __init__(
        self,
        *,
        camera: Camera | None = None,
        use_pi_camera: bool = False,
        image_path: str | Path = DEFAULT_IMAGE_PATH,
        model_path: str | Path = DEFAULT_MODEL_PATH,
        label_path: str | Path = DEFAULT_LABEL_PATH,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        nms_threshold: float = DEFAULT_NMS_THRESHOLD,
    ) -> None:
        """Create a Guardian facade.

        Args:
            camera: Optional prebuilt camera source. When omitted, Guardian
                creates a PiCamera or ImageCamera using existing Object Watch
                camera selection.
            use_pi_camera: Use the Raspberry Pi camera when no camera is
                supplied.
            image_path: Static image path used when `use_pi_camera` is False.
            model_path: ONNX model path.
            label_path: Class label file path.
            confidence_threshold: Minimum confidence for prediction decoding.
            nms_threshold: IoU threshold used by Non-Maximum Suppression.
        """
        self._camera = camera if camera is not None else create_camera(
            use_pi_camera=use_pi_camera,
            image_path=Path(image_path),
        )
        self._model_path = Path(model_path)
        self._label_path = Path(label_path)
        self._preprocessor = Preprocessor()
        self._inference_engine = InferenceEngine()
        self._detector = Detector(
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
        )
        self._started = False
        self._states: dict[str, WatchState] = {}
        self._events: dict[str, WatchEvent | None] = {}
        self._tracked_labels: set[str] = set()

    def next_frame(self) -> GuardianFrame:
        """Capture and process one frame through the existing platform."""
        self._ensure_started()

        image = self._camera.capture()
        preprocessing = self._preprocessor.process(image)
        inference = self._inference_engine.infer(preprocessing.tensor)
        predictions = tuple(self._detector.decode(inference.raw_output))
        detections = tuple(self._detector.detect(list(predictions), preprocessing))
        current_labels = frozenset(detection.label.lower() for detection in detections)
        just_detected, just_disappeared = self._update_watch_states(
            detections=detections,
            current_labels=current_labels,
        )

        return GuardianFrame(
            detections=detections,
            predictions=predictions,
            image=image,
            model_image=preprocessing.model_image,
            inference_ms=inference.inference_ms,
            _current_labels=current_labels,
            _just_detected_labels=frozenset(just_detected),
            _just_disappeared_labels=frozenset(just_disappeared),
        )

    def close(self) -> None:
        """Release owned platform resources."""
        self._camera.stop()
        self._started = False

    def _ensure_started(self) -> None:
        """Start underlying platform modules once."""
        if self._started:
            return

        self._camera.start()
        self._inference_engine.load(self._model_path)
        self._detector.load_labels(self._label_path)
        self._started = True

    def _update_watch_states(
        self,
        detections: tuple[Detection, ...],
        current_labels: frozenset[str],
    ) -> tuple[set[str], set[str]]:
        """Update Object Watch state for labels known to the facade."""
        self._tracked_labels.update(current_labels)
        just_detected: set[str] = set()
        just_disappeared: set[str] = set()

        for label in sorted(self._tracked_labels):
            previous_state = self._states.get(label, WatchState.NOT_PRESENT)
            previous_event = self._events.get(label)
            target_detection = best_target_detection(list(detections), label)

            with redirect_stdout(StringIO()):
                next_state, next_event = update_state(
                    state=previous_state,
                    active_event=previous_event,
                    target_detection=target_detection,
                    target_label=label,
                )

            if (
                previous_state is WatchState.NOT_PRESENT
                and next_state is WatchState.PRESENT
            ):
                just_detected.add(label)
            elif (
                previous_state is WatchState.PRESENT
                and next_state is WatchState.NOT_PRESENT
            ):
                just_disappeared.add(label)

            self._states[label] = next_state
            self._events[label] = next_event

        return just_detected, just_disappeared
