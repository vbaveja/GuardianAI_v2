"""Terminal operator console for GuardianAI Object Watch.

The console refreshes in place so it works over SSH without curses or external
UI libraries. It reuses the existing perception modules and Object Watch state
concepts without modifying the perception pipeline.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
import time

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from apps.object_watch import (  # noqa: E402
    DEFAULT_IMAGE_PATH,
    DEFAULT_LABEL_PATH,
    DEFAULT_MODEL_PATH,
    DEFAULT_STATIC_INTERVAL_SECONDS,
    DEFAULT_TARGET_OBJECT,
    WatchEvent,
    WatchState,
    best_target_detection,
    create_camera,
)
from src.camera import Camera  # noqa: E402
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD  # noqa: E402
from src.core.exceptions import GuardianAIError  # noqa: E402
from src.detector import Detector  # noqa: E402
from src.inference_engine import InferenceEngine  # noqa: E402
from src.preprocessing import Preprocessor  # noqa: E402
from src.types.detection import Detection  # noqa: E402


MAX_RECENT_EVENTS = 10


@dataclass(frozen=True)
class ConsoleEvent:
    """Event displayed in the GuardianAI console history."""

    timestamp: str
    object_name: str
    event_type: str
    duration_seconds: float | None = None


@dataclass(frozen=True)
class FrameResult:
    """Per-frame perception output used by the console."""

    detections: list[Detection]
    inference_ms: float


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for Guardian Console."""
    parser = argparse.ArgumentParser(description="Run the GuardianAI operator console.")
    parser.add_argument(
        "--camera",
        action="store_true",
        help="Use the Raspberry Pi camera instead of a static image.",
    )
    parser.add_argument(
        "--object",
        default=DEFAULT_TARGET_OBJECT,
        help="Object label to watch for.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        help="Minimum confidence threshold for prediction decoding.",
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the image file used when --camera is not provided.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Path to the ONNX object detector model.",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=DEFAULT_LABEL_PATH,
        help="Path to the class label file.",
    )
    parser.add_argument(
        "--nms-threshold",
        type=float,
        default=DEFAULT_NMS_THRESHOLD,
        help="IoU threshold used by Non-Maximum Suppression.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_STATIC_INTERVAL_SECONDS,
        help="Delay between frames in static image mode.",
    )
    return parser.parse_args()


def timestamp() -> str:
    """Return a readable local timestamp."""
    return datetime.now().isoformat(timespec="seconds")


def process_frame(
    camera: Camera,
    preprocessor: Preprocessor,
    inference_engine: InferenceEngine,
    detector: Detector,
) -> FrameResult:
    """Run one frame through the existing perception pipeline."""
    frame = camera.capture()
    preprocessing = preprocessor.process(frame)
    inference = inference_engine.infer(preprocessing.tensor)
    predictions = detector.decode(inference.raw_output)
    detections = detector.detect(predictions, preprocessing)
    return FrameResult(detections=detections, inference_ms=inference.inference_ms)


def visible_duration(active_event: WatchEvent | None) -> float:
    """Return how long the current target has been visible."""
    if active_event is None:
        return 0.0
    return time.perf_counter() - active_event.started_at


def update_console_state(
    state: WatchState,
    active_event: WatchEvent | None,
    target_detection: Detection | None,
    target_label: str,
    recent_events: deque[ConsoleEvent],
) -> tuple[WatchState, WatchEvent | None]:
    """Update Object Watch state and append console events on state changes."""
    if state is WatchState.NOT_PRESENT and target_detection is not None:
        event = WatchEvent(
            started_at=time.perf_counter(),
            highest_confidence=target_detection.confidence,
        )
        recent_events.append(
            ConsoleEvent(
                timestamp=timestamp(),
                object_name=target_label,
                event_type="Appeared",
            )
        )
        return WatchState.PRESENT, event

    if state is WatchState.PRESENT and target_detection is not None:
        if active_event is not None:
            active_event.highest_confidence = max(
                active_event.highest_confidence,
                target_detection.confidence,
            )
        return WatchState.PRESENT, active_event

    if state is WatchState.PRESENT and target_detection is None:
        if active_event is not None:
            recent_events.append(
                ConsoleEvent(
                    timestamp=timestamp(),
                    object_name=target_label,
                    event_type="Lost",
                    duration_seconds=visible_duration(active_event),
                )
            )
        return WatchState.NOT_PRESENT, None

    return state, active_event


def format_detection(detection: Detection) -> str:
    """Format one visible object for terminal display."""
    return (
        f"- {detection.label} | confidence={detection.confidence:.4f} | "
        f"box={detection.box}"
    )


def format_event(event: ConsoleEvent) -> str:
    """Format one recent event for terminal display."""
    if event.duration_seconds is None:
        return f"- {event.timestamp} | {event.object_name} {event.event_type}"
    return (
        f"- {event.timestamp} | {event.object_name} {event.event_type} | "
        f"duration={event.duration_seconds:.2f}s"
    )


def clear_screen() -> None:
    """Refresh the terminal without relying on curses."""
    print("\033[2J\033[H", end="")


def render_console(
    target_label: str,
    state: WatchState,
    current_confidence: float | None,
    highest_confidence: float,
    duration_seconds: float,
    inference_ms: float,
    fps: float,
    detections: list[Detection],
    recent_events: deque[ConsoleEvent],
) -> str:
    """Build the full console screen."""
    confidence_text = "n/a" if current_confidence is None else f"{current_confidence:.4f}"
    highest_text = "n/a" if highest_confidence <= 0.0 else f"{highest_confidence:.4f}"

    lines = [
        "------------------------------------------------------------",
        "GuardianAI Console",
        "",
        f"Watching: {target_label}",
        f"Current State: {state.value}",
        f"Current Confidence: {confidence_text}",
        f"Highest Confidence: {highest_text}",
        f"Visible Duration: {duration_seconds:.2f}s",
        f"Inference Time: {inference_ms:.2f} ms",
        f"FPS: {fps:.2f}",
        "",
        "------------------------------------------------------------",
        "",
        "Objects Currently Visible",
        "",
    ]

    if detections:
        lines.extend(format_detection(detection) for detection in detections)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "------------------------------------------------------------",
            "",
            "Recent Events",
            "",
        ]
    )

    if recent_events:
        lines.extend(format_event(event) for event in recent_events)
    else:
        lines.append("- none")

    lines.extend(["", "Press Ctrl+C to stop."])
    return "\n".join(lines)


def run(
    use_pi_camera: bool,
    image_path: Path,
    model_path: Path,
    label_path: Path,
    target_label: str,
    confidence_threshold: float,
    nms_threshold: float,
    interval_seconds: float,
) -> None:
    """Run the GuardianAI console until interrupted."""
    camera = create_camera(use_pi_camera, image_path)
    preprocessor = Preprocessor()
    inference_engine = InferenceEngine()
    detector = Detector(
        confidence_threshold=confidence_threshold,
        nms_threshold=nms_threshold,
    )
    state = WatchState.NOT_PRESENT
    active_event: WatchEvent | None = None
    recent_events: deque[ConsoleEvent] = deque(maxlen=MAX_RECENT_EVENTS)
    last_frame_time = time.perf_counter()

    try:
        camera.start()
        inference_engine.load(model_path)
        detector.load_labels(label_path)

        while True:
            frame_started_at = time.perf_counter()
            frame_result = process_frame(camera, preprocessor, inference_engine, detector)
            target_detection = best_target_detection(frame_result.detections, target_label)

            state, active_event = update_console_state(
                state=state,
                active_event=active_event,
                target_detection=target_detection,
                target_label=target_label,
                recent_events=recent_events,
            )

            now = time.perf_counter()
            elapsed_since_last_frame = now - last_frame_time
            fps = 1.0 / elapsed_since_last_frame if elapsed_since_last_frame > 0 else 0.0
            last_frame_time = now

            current_confidence = (
                target_detection.confidence if target_detection is not None else None
            )
            highest_confidence = (
                active_event.highest_confidence if active_event is not None else 0.0
            )

            clear_screen()
            print(
                render_console(
                    target_label=target_label,
                    state=state,
                    current_confidence=current_confidence,
                    highest_confidence=highest_confidence,
                    duration_seconds=visible_duration(active_event),
                    inference_ms=frame_result.inference_ms,
                    fps=fps,
                    detections=frame_result.detections,
                    recent_events=recent_events,
                ),
                flush=True,
            )

            if not use_pi_camera:
                elapsed = time.perf_counter() - frame_started_at
                time.sleep(max(0.0, interval_seconds - elapsed))
    except KeyboardInterrupt:
        if state is WatchState.PRESENT and active_event is not None:
            recent_events.append(
                ConsoleEvent(
                    timestamp=timestamp(),
                    object_name=target_label,
                    event_type="Lost",
                    duration_seconds=visible_duration(active_event),
                )
            )
            clear_screen()
            print(
                render_console(
                    target_label=target_label,
                    state=WatchState.NOT_PRESENT,
                    current_confidence=None,
                    highest_confidence=active_event.highest_confidence,
                    duration_seconds=0.0,
                    inference_ms=0.0,
                    fps=0.0,
                    detections=[],
                    recent_events=recent_events,
                )
            )
        print("\nStopping GuardianAI Console.")
    finally:
        camera.stop()


def main() -> int:
    """Application entry point."""
    args = parse_args()
    try:
        run(
            use_pi_camera=args.camera,
            image_path=args.image,
            model_path=args.model,
            label_path=args.labels,
            target_label=args.object,
            confidence_threshold=args.threshold,
            nms_threshold=args.nms_threshold,
            interval_seconds=args.interval,
        )
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI console error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
