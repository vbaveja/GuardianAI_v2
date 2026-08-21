"""Educational prediction explorer for GuardianAI.

This app shows how raw neural network tensors become ranked hypotheses before
Non-Maximum Suppression, labels cleanup, decisions, or hardware actions.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera import ImageCamera
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD
from src.core.exceptions import GuardianAIError
from src.detector import Detector
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor
from src.types.prediction import Prediction


DEFAULT_IMAGE_PATH = ROOT_DIR / "images" / "preprocessing_example_original.png"
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "object_detector.onnx"
DEFAULT_LABEL_PATH = ROOT_DIR / "labels" / "coco.txt"
TOP_PREDICTION_COUNT = 20


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the prediction explorer."""
    parser = argparse.ArgumentParser(description="Explore ranked YOLO predictions.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the image file to run through the model.",
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
        "--threshold",
        type=float,
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        help="Minimum class confidence required to keep a prediction.",
    )
    return parser.parse_args()


def print_educational_notes() -> None:
    """Explain what students are seeing in this sprint."""
    print("The neural network produced thousands of hypotheses.")
    print("Each hypothesis predicts where an object may exist.")
    print("Each hypothesis also predicts what class it may be.")
    print("The confidence score says how strongly the network believes it.")
    print("The detector ranks these hypotheses by confidence.")
    print("NMS has not yet been applied.")


def format_prediction(prediction: Prediction) -> str:
    """Format one prediction hypothesis for console output."""
    return (
        f"Prediction index: {prediction.index} | "
        f"Label: {prediction.label} | "
        f"Confidence: {prediction.confidence:.4f} | "
        f"Center: ({prediction.center_x:.2f}, {prediction.center_y:.2f}) | "
        f"Width: {prediction.width:.2f} | "
        f"Height: {prediction.height:.2f}"
    )


def format_box(prediction: Prediction) -> str:
    """Format the raw model-space bounding box for one prediction."""
    return (
        f"center=({prediction.center_x:.2f}, {prediction.center_y:.2f}), "
        f"width={prediction.width:.2f}, height={prediction.height:.2f}"
    )


def print_prediction_report(
    total_raw_predictions: int,
    predictions: list[Prediction],
) -> None:
    """Print the ranked prediction report."""
    print_educational_notes()
    print()
    print(f"Total raw predictions: {total_raw_predictions}")
    print(f"Predictions above threshold: {len(predictions)}")
    print(f"Top {TOP_PREDICTION_COUNT} predictions:")

    for prediction in predictions[:TOP_PREDICTION_COUNT]:
        print(format_prediction(prediction))

    print()
    print("==========")
    print("BEST PREDICTION")
    print("==========")
    if not predictions:
        print("No predictions passed the confidence threshold.")
        return

    best = predictions[0]
    print(f"Prediction Index: {best.index}")
    print(f"Label: {best.label}")
    print(f"Confidence: {best.confidence:.4f}")
    print(f"Bounding Box: {format_box(best)}")


def run(
    image_path: Path,
    model_path: Path,
    label_path: Path,
    confidence_threshold: float,
) -> None:
    """Run preprocessing, inference, and first-stage prediction decoding."""
    camera = ImageCamera(image_path)
    preprocessor = Preprocessor()
    inference_engine = InferenceEngine()
    detector = Detector(confidence_threshold=confidence_threshold)

    try:
        camera.start()
        frame = camera.capture()
        preprocessing = preprocessor.process(frame)

        inference_engine.load(model_path)
        inference = inference_engine.infer(preprocessing.tensor)

        detector.load_labels(label_path)
        total_raw_predictions = detector.count_raw_predictions(inference.raw_output)
        predictions = detector.decode(inference.raw_output)

        print_prediction_report(total_raw_predictions, predictions)
    finally:
        camera.stop()


def main() -> int:
    """Application entry point."""
    args = parse_args()
    try:
        run(
            image_path=args.image,
            model_path=args.model,
            label_path=args.labels,
            confidence_threshold=args.threshold,
        )
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI prediction explorer error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
