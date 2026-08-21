"""Educational raw inference explorer for GuardianAI.

This app shows students that a neural network returns numeric tensors before
any labels, filtering, or object-detection decoding happen.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera import ImageCamera
from src.core.exceptions import GuardianAIError
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor
from src.types.inference import InferenceResult


WINDOW_NAME = "GuardianAI Inference Explorer"
DEFAULT_IMAGE_PATH = ROOT_DIR / "images" / "preprocessing_example_original.png"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the inference explorer."""
    parser = argparse.ArgumentParser(description="Explore raw ONNX model output.")
    parser.add_argument("model_path", type=Path, help="Path to an ONNX model.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the image file to run through the model.",
    )
    return parser.parse_args()


def _first_output_array(result: InferenceResult) -> np.ndarray:
    """Return the first output tensor as a NumPy array."""
    raw_output = result.raw_output
    if isinstance(raw_output, list | tuple):
        if not raw_output:
            raise ValueError("Inference produced no output tensors.")
        return np.asarray(raw_output[0])
    return np.asarray(raw_output)


def _prediction_vectors(output: np.ndarray) -> np.ndarray:
    """View an output tensor as prediction vectors.

    YOLO-style exports commonly produce either (1, 84, N) or (1, N, 84).
    GuardianAI presents both layouts as (N, 84): one row per prediction.
    """
    if output.ndim == 0:
        return output.reshape(1, 1)
    if output.ndim == 1:
        return output.reshape(-1, 1)
    if output.ndim == 3 and output.shape[0] == 1:
        if output.shape[1] == 84:
            return np.transpose(output[0], (1, 0))
        if output.shape[2] == 84:
            return output[0]
    return output.reshape(-1, output.shape[-1])


def _format_vector(vectors: np.ndarray, prediction_number: int) -> str:
    """Format one prediction vector or explain why it is unavailable."""
    index = prediction_number - 1
    if index >= len(vectors):
        return (
            f"Prediction #{prediction_number}: unavailable; "
            f"only {len(vectors)} predictions"
        )

    vector_text = np.array2string(
        vectors[index],
        precision=4,
        threshold=24,
        edgeitems=8,
        suppress_small=False,
    )
    return f"Prediction #{prediction_number}: {vector_text}"


def print_inference_debug(
    model_path: Path,
    input_tensor: np.ndarray,
    result: InferenceResult,
) -> None:
    """Print educational information about raw neural network output."""
    output = _first_output_array(result)
    vectors = _prediction_vectors(output)

    print(f"Model name: {model_path.name}")
    print(f"Input tensor shape: {input_tensor.shape}")
    print(f"Output tensor shape: {output.shape}")
    print(f"Number of predictions: {len(vectors)}")
    print(f"Values per prediction: {vectors.shape[1]}")
    print(f"Tensor dtype: {output.dtype}")
    print(f"Inference time: {result.inference_ms:.2f} ms")
    print(f"Minimum value: {float(output.min()):.6f}")
    print(f"Maximum value: {float(output.max()):.6f}")
    print(f"Mean value: {float(output.mean()):.6f}")
    print(_format_vector(vectors, 1))
    print(_format_vector(vectors, 100))
    print(_format_vector(vectors, 1000))


def run(model_path: Path, image_path: Path) -> None:
    """Run preprocessing and raw model inference for one image."""
    camera = ImageCamera(image_path)
    preprocessor = Preprocessor()
    inference_engine = InferenceEngine()

    try:
        camera.start()
        frame = camera.capture()
        preprocessing = preprocessor.process(frame)

        inference_engine.load(model_path)
        inference = inference_engine.infer(preprocessing.tensor)
        print_inference_debug(model_path, preprocessing.tensor, inference)

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.imshow(WINDOW_NAME, frame)
        cv2.waitKey(0)
    finally:
        camera.stop()
        cv2.destroyAllWindows()


def main() -> int:
    """Application entry point."""
    args = parse_args()
    try:
        run(args.model_path, args.image)
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI inference explorer error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
