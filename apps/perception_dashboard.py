"""Integrated perception dashboard for GuardianAI.

The dashboard combines the earlier educational explorers into one visual view
so students can see how an image becomes predictions and final detections.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import time

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera import Camera, ImageCamera, PiCamera
from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD
from src.core.exceptions import GuardianAIError
from src.detector import Detector
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor
from src.types.detection import Detection
from src.types.inference import InferenceResult
from src.types.prediction import Prediction
from src.types.preprocessing import PreprocessingResult


WINDOW_NAME = "GuardianAI Perception Dashboard"
DEFAULT_IMAGE_PATH = ROOT_DIR / "images" / "preprocessing_example_original.png"
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "object_detector.onnx"
DEFAULT_LABEL_PATH = ROOT_DIR / "labels" / "coco.txt"
PANEL_WIDTH = 420
PANEL_HEIGHT = 280
INFO_HEIGHT = 230
PREDICTION_COLOR = (255, 180, 0)
DETECTION_COLOR = (0, 255, 80)
HIGHLIGHT_COLOR = (0, 255, 255)
TEXT_COLOR = (235, 235, 235)
BACKGROUND_COLOR = (28, 28, 28)


@dataclass(frozen=True)
class DashboardData:
    """Reusable pipeline outputs displayed by the dashboard."""

    frame: np.ndarray
    preprocessing: PreprocessingResult
    inference: InferenceResult
    raw_prediction_count: int
    predictions: list[Prediction]
    detections: list[Detection]
    confidence_threshold: float
    source_name: str
    fps: float
    paused: bool


STAGE_TITLES = {
    1: "Original Image",
    2: "Grayscale",
    3: "Edge Detection",
    4: "Model Input",
    5: "Prediction View",
    6: "Final Detection View",
}

STAGE_EXPLANATIONS = {
    1: "The camera frame is the starting point: raw pixels from the world.",
    2: "Grayscale removes color so brightness patterns become easier to see.",
    3: "Edges highlight sharp brightness changes around object boundaries.",
    4: "The model input is letterboxed and resized before the neural network sees it.",
    5: "Predictions are raw hypotheses above the confidence threshold.",
    6: "Detections are final objects after NMS removes duplicate predictions.",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the perception dashboard."""
    parser = argparse.ArgumentParser(description="Show GuardianAI perception stages.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the image file to run through the dashboard.",
    )
    parser.add_argument(
        "--camera",
        action="store_true",
        help="Use the Raspberry Pi camera instead of a static image.",
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
        help="Minimum confidence threshold for prediction decoding.",
    )
    parser.add_argument(
        "--nms-threshold",
        type=float,
        default=DEFAULT_NMS_THRESHOLD,
        help="IoU threshold used by Non-Maximum Suppression.",
    )
    return parser.parse_args()


def process_frame(
    frame: np.ndarray,
    preprocessor: Preprocessor,
    inference_engine: InferenceEngine,
    detector: Detector,
    confidence_threshold: float,
    source_name: str,
    fps: float,
    paused: bool,
) -> DashboardData:
    """Run one frame through the reusable perception modules."""
    preprocessing = preprocessor.process(frame)
    inference = inference_engine.infer(preprocessing.tensor)
    raw_prediction_count = detector.count_raw_predictions(inference.raw_output)
    predictions = detector.decode(inference.raw_output)
    detections = detector.detect(predictions, preprocessing)

    return DashboardData(
        frame=frame,
        preprocessing=preprocessing,
        inference=inference,
        raw_prediction_count=raw_prediction_count,
        predictions=predictions,
        detections=detections,
        confidence_threshold=confidence_threshold,
        source_name=source_name,
        fps=fps,
        paused=paused,
    )


def draw_title(panel: np.ndarray, title: str, highlighted: bool) -> np.ndarray:
    """Draw a readable panel title and optional highlight border."""
    cv2.rectangle(panel, (0, 0), (panel.shape[1] - 1, 30), BACKGROUND_COLOR, -1)
    cv2.putText(panel, title, (10, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.62, TEXT_COLOR, 1, cv2.LINE_AA)
    border_color = HIGHLIGHT_COLOR if highlighted else (80, 80, 80)
    border_width = 4 if highlighted else 1
    cv2.rectangle(panel, (0, 0), (panel.shape[1] - 1, panel.shape[0] - 1), border_color, border_width)
    return panel


def resize_for_panel(image: np.ndarray) -> np.ndarray:
    """Resize an image into the standard panel area."""
    return cv2.resize(image, (PANEL_WIDTH, PANEL_HEIGHT), interpolation=cv2.INTER_AREA)


def make_panel(image: np.ndarray, title: str, highlighted: bool) -> np.ndarray:
    """Create one titled dashboard panel."""
    panel = resize_for_panel(image)
    return draw_title(panel, title, highlighted)


def grayscale_panel(frame: np.ndarray) -> np.ndarray:
    """Create the grayscale educational view."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def edges_panel(frame: np.ndarray) -> np.ndarray:
    """Create the edge-detection educational view."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def prediction_box(prediction: Prediction) -> tuple[int, int, int, int]:
    """Convert a prediction center box into model-input corner coordinates."""
    half_width = prediction.width / 2.0
    half_height = prediction.height / 2.0
    return (
        int(round(prediction.center_x - half_width)),
        int(round(prediction.center_y - half_height)),
        int(round(prediction.center_x + half_width)),
        int(round(prediction.center_y + half_height)),
    )


def draw_predictions(model_image: np.ndarray, predictions: list[Prediction]) -> np.ndarray:
    """Draw every prediction hypothesis on the model-input image."""
    view = model_image.copy()
    for prediction in predictions:
        x1, y1, x2, y2 = prediction_box(prediction)
        cv2.rectangle(view, (x1, y1), (x2, y2), PREDICTION_COLOR, 1)
    return view


def draw_detections(frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Draw final detections on the original image."""
    view = frame.copy()
    for detection in detections:
        x1, y1, x2, y2 = detection.box
        cv2.rectangle(view, (x1, y1), (x2, y2), DETECTION_COLOR, 2)
        label = f"{detection.label} {detection.confidence:.2f}"
        cv2.putText(view, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, DETECTION_COLOR, 2)
    return view


def add_prediction_summary(
    panel: np.ndarray,
    predictions: list[Prediction],
    confidence_threshold: float,
) -> np.ndarray:
    """Overlay prediction metrics on the prediction panel."""
    top_confidence = predictions[0].confidence if predictions else 0.0
    lines = [
        f"Prediction count: {len(predictions)}",
        f"Threshold: {confidence_threshold:.2f}",
        f"Top confidence: {top_confidence:.3f}",
    ]
    return draw_text_block(panel, lines, 12, 48)


def add_detection_summary(panel: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Overlay final detection metrics on the detection panel."""
    lines = [f"Final detections: {len(detections)}"]
    return draw_text_block(panel, lines, 12, 48)


def draw_text_block(panel: np.ndarray, lines: list[str], x: int, y: int) -> np.ndarray:
    """Draw readable text over a translucent dark rectangle."""
    if not lines:
        return panel

    overlay = panel.copy()
    height = 24 * len(lines) + 12
    cv2.rectangle(overlay, (x - 6, y - 20), (x + 290, y - 20 + height), BACKGROUND_COLOR, -1)
    panel = cv2.addWeighted(overlay, 0.72, panel, 0.28, 0)

    for index, line in enumerate(lines):
        cv2.putText(
            panel,
            line,
            (x, y + index * 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            TEXT_COLOR,
            1,
            cv2.LINE_AA,
        )
    return panel


def make_info_panel(data: DashboardData, active_stage: int) -> np.ndarray:
    """Create the dashboard information panel."""
    panel = np.full((INFO_HEIGHT, PANEL_WIDTH * 3, 3), BACKGROUND_COLOR, dtype=np.uint8)
    image_height, image_width = data.preprocessing.original_shape
    tensor_shape = getattr(data.preprocessing.tensor, "shape", "unknown")
    predictions_after_nms = len(data.detections)

    lines = [
        "Information Panel",
        f"Current layer: {STAGE_TITLES[active_stage]}",
        f"Source: {data.source_name}",
        f"Status: {'Paused' if data.paused else 'Running'}",
        f"Image size: {image_width}x{image_height}",
        f"Tensor size: {tensor_shape}",
        f"Live FPS: {data.fps:.2f}",
        f"Inference time: {data.inference.inference_ms:.2f} ms",
        f"Raw predictions: {data.raw_prediction_count}",
        f"Predictions after threshold: {len(data.predictions)}",
        f"Predictions after NMS: {predictions_after_nms}",
        f"Explanation: {STAGE_EXPLANATIONS[active_stage]}",
        "Keys: 1-6 stage focus | P predictions | D detections | Space pause/resume | Q quit",
    ]

    y = 28
    for index, line in enumerate(lines):
        font_scale = 0.72 if index == 0 else 0.56
        color = HIGHLIGHT_COLOR if index == 0 else TEXT_COLOR
        cv2.putText(panel, line, (14, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1, cv2.LINE_AA)
        y += 24 if index else 30
    return panel


def render_dashboard(data: DashboardData, active_stage: int) -> np.ndarray:
    """Render the complete multi-panel dashboard."""
    prediction_view = draw_predictions(data.preprocessing.model_image, data.predictions)
    detection_view = draw_detections(data.frame, data.detections)

    panels = [
        make_panel(data.frame, STAGE_TITLES[1], active_stage == 1),
        make_panel(grayscale_panel(data.frame), STAGE_TITLES[2], active_stage == 2),
        make_panel(edges_panel(data.frame), STAGE_TITLES[3], active_stage == 3),
        make_panel(data.preprocessing.model_image, STAGE_TITLES[4], active_stage == 4),
        add_prediction_summary(
            make_panel(prediction_view, STAGE_TITLES[5], active_stage == 5),
            data.predictions,
            data.confidence_threshold,
        ),
        add_detection_summary(
            make_panel(detection_view, STAGE_TITLES[6], active_stage == 6),
            data.detections,
        ),
    ]

    first_row = np.hstack(panels[:3])
    second_row = np.hstack(panels[3:])
    info_row = make_info_panel(data, active_stage)
    return np.vstack([first_row, second_row, info_row])


def next_stage(active_stage: int) -> int:
    """Advance to the next dashboard stage."""
    return 1 if active_stage >= 6 else active_stage + 1


def create_camera(use_pi_camera: bool, image_path: Path) -> Camera:
    """Create the selected dashboard frame source."""
    if use_pi_camera:
        return PiCamera()
    return ImageCamera(image_path)


def run(
    image_path: Path,
    model_path: Path,
    label_path: Path,
    confidence_threshold: float,
    nms_threshold: float,
    use_pi_camera: bool,
) -> None:
    """Run the interactive perception dashboard."""
    camera = create_camera(use_pi_camera, image_path)
    preprocessor = Preprocessor()
    inference_engine = InferenceEngine()
    detector = Detector(
        confidence_threshold=confidence_threshold,
        nms_threshold=nms_threshold,
    )
    source_name = "PiCamera" if use_pi_camera else f"ImageCamera: {image_path.name}"

    active_stage = 1
    paused = False
    data: DashboardData | None = None
    last_frame_time = time.perf_counter()

    try:
        camera.start()
        inference_engine.load(model_path)
        detector.load_labels(label_path)

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        while True:
            if data is None or (use_pi_camera and not paused):
                frame = camera.capture()
                now = time.perf_counter()
                elapsed = now - last_frame_time
                fps = 1.0 / elapsed if elapsed > 0 else 0.0
                last_frame_time = now
                data = process_frame(
                    frame=frame,
                    preprocessor=preprocessor,
                    inference_engine=inference_engine,
                    detector=detector,
                    confidence_threshold=confidence_threshold,
                    source_name=source_name,
                    fps=fps,
                    paused=paused,
                )
            elif data is not None and data.paused != paused:
                data = DashboardData(
                    frame=data.frame,
                    preprocessing=data.preprocessing,
                    inference=data.inference,
                    raw_prediction_count=data.raw_prediction_count,
                    predictions=data.predictions,
                    detections=data.detections,
                    confidence_threshold=data.confidence_threshold,
                    source_name=data.source_name,
                    fps=0.0 if paused else data.fps,
                    paused=paused,
                )

            cv2.imshow(WINDOW_NAME, render_dashboard(data, active_stage))
            key_code = cv2.waitKey(50) & 0xFF
            if key_code == 255:
                if not use_pi_camera:
                    continue
                continue

            key = chr(key_code).lower()
            if key == "q":
                break
            if key in {"1", "2", "3", "4", "5", "6"}:
                active_stage = int(key)
            elif key == "p":
                active_stage = 5
            elif key == "d":
                active_stage = 6
            elif key == " ":
                paused = not paused
    except KeyboardInterrupt:
        print("Stopping GuardianAI perception dashboard.")
    finally:
        camera.stop()
        cv2.destroyAllWindows()


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
            use_pi_camera=args.camera,
        )
    except (GuardianAIError, FileNotFoundError, ValueError) as error:
        print(f"GuardianAI perception dashboard error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
