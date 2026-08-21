"""Educational detection explorer for GuardianAI.

This app shows how ranked prediction hypotheses become final detections after
Non-Maximum Suppression and coordinate restoration.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera import ImageCamera
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD
from src.core.exceptions import GuardianAIError
from src.detector import Detector
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor
from src.types.detection import Detection


DEFAULT_IMAGE_PATH = ROOT_DIR / "images" / "preprocessing_example_original.png"
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "object_detector.onnx"
DEFAULT_LABEL_PATH = ROOT_DIR / "labels" / "coco.txt"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the detection explorer."""
    parser = argparse.ArgumentParser(description="Explore YOLO detection stages.")
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
    parser.add_argument(
        "--nms-threshold",
        type=float,
        default=DEFAULT_NMS_THRESHOLD,
        help="IoU threshold used by Non-Maximum Suppression.",
    )
    return parser.parse_args()


def print_educational_notes() -> None:
    """Explain the detection concepts introduced in Sprint 7."""
    print("IoU means Intersection over Union.")
    print("It measures how much two boxes overlap compared with their total area.")
    print("Duplicate predictions occur because YOLO tests many nearby hypotheses.")
    print("NMS is required because several hypotheses may describe the same object.")
    print("The strongest prediction survives because it has the highest confidence.")
    print()


def format_detection(detection: Detection) -> str:
    """Format one final detection for console output."""
    return (
        f"Label: {detection.label} | "
        f"Confidence: {detection.confidence:.4f} | "
        f"Box: {detection.box}"
    )


def print_detection_report(
    total_raw_hypotheses: int,
    predictions_after_threshold: int,
    nms_removal_explanations: tuple[str, ...],
    detections: list[Detection],
) -> None:
    """Print every educational stage of prediction-to-detection conversion."""
    print_educational_notes()

    print("Stage 1")
    print("--------")
    print(f"Total raw hypotheses: {total_raw_hypotheses}")
    print()

    print("Stage 2")
    print("--------")
    print(f"Predictions after confidence threshold: {predictions_after_threshold}")
    print()

    print("Stage 3")
    print("--------")
    print(f"Predictions before NMS: {predictions_after_threshold}")
    print()

    print("Stage 4")
    print("--------")
    print(f"Predictions removed by NMS: {len(nms_removal_explanations)}")
    if nms_removal_explanations:
        for explanation in nms_removal_explanations:
            print()
            print(explanation)
    else:
        print("No predictions were removed by NMS.")
    print()

    print("Stage 5")
    print("--------")
    print("Final Detection list")
    if not detections:
        print("No final detections.")
        return

    for detection in detections:
        print(format_detection(detection))


def run(
    image_path: Path,
    model_path: Path,
    label_path: Path,
    confidence_threshold: float,
    nms_threshold: float,
) -> None:
    """Run the full image-to-detection educational pipeline."""
    camera = ImageCamera(image_path)
    preprocessor = Preprocessor()
    inference_engine = InferenceEngine()
    detector = Detector(
        confidence_threshold=confidence_threshold,
        nms_threshold=nms_threshold,
    )

    try:
        camera.start()
        frame = camera.capture()
        preprocessing = preprocessor.process(frame)

        inference_engine.load(model_path)
        inference = inference_engine.infer(preprocessing.tensor)

        detector.load_labels(label_path)
        total_raw_hypotheses = detector.count_raw_predictions(inference.raw_output)
        predictions = detector.decode(inference.raw_output)
        detections = detector.detect(predictions, preprocessing)

        print_detection_report(
            total_raw_hypotheses=total_raw_hypotheses,
            predictions_after_threshold=len(predictions),
            nms_removal_explanations=detector.last_nms_explanations,
            detections=detections,
        )
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
            nms_threshold=args.nms_threshold,
        )
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI detection explorer error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
