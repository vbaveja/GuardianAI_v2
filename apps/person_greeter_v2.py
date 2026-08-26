"""Person Greeter implemented with the Guardian facade."""

from __future__ import annotations

import argparse
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
)
from apps.person_greeter import DEFAULT_SOUND_PATH, display_label, play_greeting  # noqa: E402
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD  # noqa: E402
from src.core.exceptions import GuardianAIError  # noqa: E402
from src.guardian import Guardian  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for Person Greeter v2."""
    parser = argparse.ArgumentParser(
        description="Play one greeting when a watched object appears."
    )
    parser.add_argument(
        "--camera",
        action="store_true",
        help="Use the Raspberry Pi camera instead of a static image.",
    )
    parser.add_argument(
        "--object",
        default=DEFAULT_TARGET_OBJECT,
        help="Object label to greet when it appears.",
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
        help="Path to the WAV greeting sound.",
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


def run(
    use_pi_camera: bool,
    image_path: Path,
    model_path: Path,
    label_path: Path,
    target_label: str,
    confidence_threshold: float,
    nms_threshold: float,
    sound_path: Path,
    interval_seconds: float,
) -> None:
    """Run Person Greeter v2 until interrupted."""
    guardian = Guardian(
        use_pi_camera=use_pi_camera,
        image_path=image_path,
        model_path=model_path,
        label_path=label_path,
        confidence_threshold=confidence_threshold,
        nms_threshold=nms_threshold,
    )
    label_text = display_label(target_label)
    announced_visible = False

    print(f"Watching for object: {target_label}")
    print(f"Sound: {sound_path}")
    print(f"Source: {'PiCamera' if use_pi_camera else image_path}")
    print("Press Ctrl+C to stop.")
    print()
    print(f"Waiting for {target_label}...")

    try:
        while True:
            frame_started_at = time.perf_counter()
            frame = guardian.next_frame()

            if frame.just_detected(target_label):
                announced_visible = False
                print(f"{label_text} detected.")
                print("Playing greeting...")
                play_greeting(sound_path)
            elif frame.sees(target_label):
                if not announced_visible:
                    print(f"{label_text} still visible.")
                    announced_visible = True
            elif frame.just_disappeared(target_label):
                announced_visible = False
                print(f"{label_text} left.")
                print("Waiting again...")

            if not use_pi_camera:
                elapsed = time.perf_counter() - frame_started_at
                time.sleep(max(0.0, interval_seconds - elapsed))
    except KeyboardInterrupt:
        print("\nStopping Person Greeter.")
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
            interval_seconds=args.interval,
        )
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI person greeter error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
