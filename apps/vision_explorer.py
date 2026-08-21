"""Educational image pipeline explorer for GuardianAI.

Vision Explorer shows how one image changes as it moves through early computer
vision transformations and into the neural-network input format.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import cv2

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera import ImageCamera
from src.core.exceptions import GuardianAIError
from src.preprocessing import Preprocessor
from src.types.preprocessing import PreprocessingResult


WINDOW_NAME = "GuardianAI Vision Explorer"
DEFAULT_IMAGE_PATH = ROOT_DIR / "images" / "preprocessing_example_original.png"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the Vision Explorer app."""
    parser = argparse.ArgumentParser(description="Explore GuardianAI vision layers.")
    parser.add_argument(
        "image_path",
        nargs="?",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the image file to explore.",
    )
    return parser.parse_args()


def render_layer(key: str, frame, result: PreprocessingResult):
    """Render the selected educational visualization layer."""
    if key == "1":
        return frame

    if key == "2":
        # Grayscale removes color so students can focus on brightness.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    if key == "3":
        # Blur removes fine detail and reduces noise before later analysis.
        return cv2.GaussianBlur(frame, (9, 9), 0)

    if key == "4":
        # Edges show where brightness changes sharply, often around objects.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    if key == "5":
        # Motion requires multiple frames. ImageCamera is static, so this layer
        # intentionally teaches that change needs time-based comparison.
        placeholder = frame.copy()
        cv2.putText(
            placeholder,
            "Motion requires multiple frames",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return placeholder

    if key == "6":
        # This is the exact letterboxed image sent into the neural network.
        return result.model_image

    return frame


def print_debug_info(result: PreprocessingResult) -> None:
    """Print preprocessing values that define the model input contract."""
    print(f"Original shape: {result.original_shape}")
    print(f"Model image shape: {result.model_image.shape}")
    print(f"Tensor shape: {result.tensor.shape}")
    print(f"Scale: {result.scale}")
    print(f"Padding: pad_x={result.pad_x}, pad_y={result.pad_y}")


def print_keyboard_help() -> None:
    """Print supported Vision Explorer keys."""
    print("GuardianAI Vision Explorer")
    print("1: Original image")
    print("2: Grayscale")
    print("3: Blurred image")
    print("4: Edge detection")
    print("5: Motion placeholder")
    print("6: Model input image")
    print("d: Debug information")
    print("q: Quit")


def run(image_path: Path) -> None:
    """Run the Vision Explorer application."""
    camera = ImageCamera(image_path)
    preprocessor = Preprocessor()
    active_key = "1"

    try:
        camera.start()
        frame = camera.capture()
        result = preprocessor.process(frame)

        print_keyboard_help()
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        while True:
            cv2.imshow(WINDOW_NAME, render_layer(active_key, frame, result))
            key_code = cv2.waitKey(50) & 0xFF
            if key_code == 255:
                continue

            key = chr(key_code)
            if key == "q":
                break
            if key in {"1", "2", "3", "4", "5", "6"}:
                active_key = key
            elif key == "d":
                print_debug_info(result)
    finally:
        camera.stop()
        cv2.destroyAllWindows()


def main() -> int:
    """Application entry point."""
    args = parse_args()
    try:
        run(args.image_path)
    except GuardianAIError as error:
        print(f"GuardianAI error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
