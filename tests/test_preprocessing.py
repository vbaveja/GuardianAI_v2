"""Manual preprocessing test for GuardianAI.

This script creates and loads a deterministic example image, runs the
preprocessor, prints the important tensor contract values, and saves the exact
image sent to the neural network for student inspection.
"""

from pathlib import Path
import sys

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.preprocessing import Preprocessor


IMAGES_DIR = ROOT_DIR / "images"
EXAMPLE_IMAGE_PATH = IMAGES_DIR / "preprocessing_example_original.png"
MODEL_IMAGE_PATH = IMAGES_DIR / "preprocessing_model_image.png"


def _create_example_image(path: Path) -> None:
    """Create a simple, deterministic BGR image for preprocessing inspection."""
    image = np.zeros((360, 640, 3), dtype=np.uint8)

    # The colored shapes make stretching or padding easy to see by eye.
    image[:, :] = (35, 35, 35)
    cv2.rectangle(image, (60, 60), (260, 300), (0, 200, 80), thickness=-1)
    cv2.circle(image, (450, 180), 90, (220, 80, 40), thickness=-1)
    cv2.line(image, (0, 0), (639, 359), (255, 255, 255), thickness=4)

    cv2.imwrite(str(path), image)


def test_preprocessing_contract() -> None:
    """Run preprocessing and print the core data contract values."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if not EXAMPLE_IMAGE_PATH.exists():
        _create_example_image(EXAMPLE_IMAGE_PATH)

    frame = cv2.imread(str(EXAMPLE_IMAGE_PATH))
    result = Preprocessor().process(frame)

    cv2.imwrite(str(MODEL_IMAGE_PATH), result.model_image)

    print(f"Original shape: {result.original_shape}")
    print(f"Model image shape: {result.model_image.shape}")
    print(f"Tensor shape: {result.tensor.shape}")
    print(f"Scale: {result.scale}")
    print(f"Padding: pad_x={result.pad_x}, pad_y={result.pad_y}")
    print(f"Saved model image: {MODEL_IMAGE_PATH}")

    assert result.original_shape == (360, 640)
    assert result.model_image.shape == (640, 640, 3)
    assert result.tensor.shape == (1, 3, 640, 640)
    assert result.tensor.dtype == np.float32
    assert 0.0 <= float(result.tensor.min()) <= 1.0
    assert 0.0 <= float(result.tensor.max()) <= 1.0
    assert MODEL_IMAGE_PATH.exists()


if __name__ == "__main__":
    test_preprocessing_contract()
