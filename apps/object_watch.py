"""Watch for a target object using the GuardianAI perception pipeline.

Object Watch is the first GuardianAI application that turns detections into
application-level events. It intentionally keeps the state machine local to
this app and does not introduce GPIO, decisions, actions, or new framework
layers.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera import Camera, ImageCamera, PiCamera
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD
from src.core.exceptions import GuardianAIError
from src.detector import Detector
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor
from src.types.detection import Detection


DEFAULT_IMAGE_PATH = ROOT_DIR / "images" / "preprocessing_example_original.png"
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "object_detector.onnx"
DEFAULT_LABEL_PATH = ROOT_DIR / "labels" / "coco.txt"
DEFAULT_TARGET_OBJECT = "person"
DEFAULT_STATIC_INTERVAL_SECONDS = 3.0
DEFAULT_SOUND_PATH = ROOT_DIR / "sounds" / "hello.wav"
DEFAULT_WATCH_MODE = "once"
WATCH_MODES = ("once", "continuous")


class WatchState(Enum):
    """Application-level state for target object visibility."""

    NOT_PRESENT = "NOT_PRESENT"
    PRESENT = "PRESENT"


@dataclass
class WatchEvent:
    """Mutable event state tracked while a target remains visible."""

    started_at: float
    highest_confidence: float


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for Object Watch."""
    parser = argparse.ArgumentParser(
        description="Watch for one object and optionally play a sound."
    )
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
        "--sound",
        type=Path,
        default=DEFAULT_SOUND_PATH,
        help="Path to the WAV sound to play when the object is visible.",
    )
    parser.add_argument(
        "--mode",
        choices=WATCH_MODES,
        default=DEFAULT_WATCH_MODE,
        help="Sound mode: once per appearance or continuously while visible.",
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


def create_camera(use_pi_camera: bool, image_path: Path) -> Camera:
    """Create the selected frame source."""
    if use_pi_camera:
        return PiCamera()
    return ImageCamera(image_path)


def timestamp() -> str:
    """Return a readable local timestamp for console events."""
    return datetime.now().isoformat(timespec="seconds")


def best_target_detection(
    detections: list[Detection],
    target_label: str,
) -> Detection | None:
    """Find the highest-confidence detection matching the target label."""
    matching_detections = [
        detection
        for detection in detections
        if detection.label.lower() == target_label.lower()
    ]
    if not matching_detections:
        return None
    return max(matching_detections, key=lambda detection: detection.confidence)


def process_frame(
    frame,
    preprocessor: Preprocessor,
    inference_engine: InferenceEngine,
    detector: Detector,
) -> list[Detection]:
    """Run one frame through the existing perception pipeline."""
    preprocessing = preprocessor.process(frame)
    inference = inference_engine.infer(preprocessing.tensor)
    predictions = detector.decode(inference.raw_output)
    return detector.detect(predictions, preprocessing)


def print_present_event(target_label: str, detection: Detection) -> None:
    """Print the event emitted when the target first appears."""
    print(f"[{timestamp()}] PRESENT")
    print(f"Object: {target_label}")
    print(f"Confidence: {detection.confidence:.4f}")
    print()


def print_not_present_event(event: WatchEvent) -> None:
    """Print the event emitted when the target disappears."""
    visible_duration = time.perf_counter() - event.started_at
    print(f"[{timestamp()}] NOT_PRESENT")
    print(f"Total visible duration: {visible_duration:.2f} seconds")
    print(f"Highest confidence observed: {event.highest_confidence:.4f}")
    print()


def display_label(label: str) -> str:
    """Return a readable object label for console messages."""
    return label[:1].upper() + label[1:]


def play_sound(sound_path: Path) -> None:
    """Play a WAV sound with Linux aplay when available."""
    if not sound_path.exists():
        print(f"Warning: sound file not found: {sound_path}")
        return

    audio_player = shutil.which("aplay")
    if audio_player is None:
        print("Warning: audio player 'aplay' not found. Sound skipped.")
        return

    try:
        subprocess.run(
            [audio_player, "-q", str(sound_path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as error:
        print(f"Warning: sound playback failed: {error}")


def update_state(
    state: WatchState,
    active_event: WatchEvent | None,
    target_detection: Detection | None,
    target_label: str,
) -> tuple[WatchState, WatchEvent | None]:
    """Update the object visibility state machine for one frame."""
    if state is WatchState.NOT_PRESENT and target_detection is not None:
        event = WatchEvent(
            started_at=time.perf_counter(),
            highest_confidence=target_detection.confidence,
        )
        print_present_event(target_label, target_detection)
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
            print_not_present_event(active_event)
        return WatchState.NOT_PRESENT, None

    return state, active_event


def run(
    use_pi_camera: bool,
    image_path: Path,
    model_path: Path,
    label_path: Path,
    target_label: str,
    confidence_threshold: float,
    nms_threshold: float,
    sound_path: Path,
    mode: str,
    interval_seconds: float,
) -> None:
    """Run Object Watch until interrupted."""
    from src.guardian import Guardian

    guardian = Guardian(
        use_pi_camera=use_pi_camera,
        image_path=image_path,
        model_path=model_path,
        label_path=label_path,
        confidence_threshold=confidence_threshold,
        nms_threshold=nms_threshold,
    )
    label_text = display_label(target_label)
    next_sound_at = 0.0
    announced_visible = False

    print(f"Watching for object: {target_label}")
    print(f"Mode: {mode}")
    print(f"Sound: {sound_path}")
    print(f"Source: {'PiCamera' if use_pi_camera else image_path}")
    print("Press Ctrl+C to stop.")
    print()
    print(f"Waiting for {target_label}...")

    try:
        while True:
            frame_started_at = time.perf_counter()
            frame = guardian.next_frame()
            now = time.perf_counter()

            if frame.just_detected(target_label):
                announced_visible = False
                next_sound_at = now + interval_seconds
                print(f"{label_text} detected.")
                print("Playing sound...")
                play_sound(sound_path)
            elif frame.sees(target_label):
                if mode == "continuous" and now >= next_sound_at:
                    print(f"{label_text} still visible.")
                    print("Playing sound...")
                    play_sound(sound_path)
                    next_sound_at = now + interval_seconds
                elif mode == "once" and not announced_visible:
                    print(f"{label_text} still visible.")
                    announced_visible = True
            elif frame.just_disappeared(target_label):
                announced_visible = False
                next_sound_at = 0.0
                print(f"{label_text} left.")
                print("Waiting again...")

            if not use_pi_camera:
                elapsed = time.perf_counter() - frame_started_at
                time.sleep(max(0.0, interval_seconds - elapsed))
    except KeyboardInterrupt:
        print("Stopping Object Watch.")
    finally:
        guardian.close()


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
            sound_path=args.sound,
            mode=args.mode,
            interval_seconds=args.interval,
        )
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI object watch error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
