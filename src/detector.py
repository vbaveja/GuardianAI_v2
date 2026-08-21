"""Two-stage prediction and detection pipeline for GuardianAI.

Prediction = raw neural-network hypothesis. It says where an object may exist,
which class is most likely, and how confident the network is.

Detection = final accepted object after filtering, Non-Maximum Suppression, and
coordinate restoration to the original image.

Current architecture:

Inference Engine
        |
        v
decode()
        |
        v
Prediction List
        |
        v
detect()
        |
        v
Detection List
"""

from pathlib import Path
from typing import Any

import numpy as np

from src.core.constants import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_NMS_THRESHOLD
from src.core.exceptions import DetectionError
from src.types.detection import Detection
from src.types.prediction import Prediction
from src.types.preprocessing import PreprocessingResult


class Detector:
    """Decode predictions and convert them into final detections.

    Prediction decoding teaches how raw tensors become hypotheses. Detection
    teaches how duplicate hypotheses collapse into final accepted objects.
    """

    def __init__(
        self,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        nms_threshold: float = DEFAULT_NMS_THRESHOLD,
    ) -> None:
        """Create a detector with configurable filtering thresholds.

        Args:
            confidence_threshold: Minimum class confidence required to keep a
                prediction hypothesis.
            nms_threshold: IoU threshold above which a lower-confidence
                prediction is treated as a duplicate.

        Raises:
            DetectionError: If a threshold is outside the 0.0-1.0 range.
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise DetectionError("Confidence threshold must be between 0.0 and 1.0.")
        if not 0.0 <= nms_threshold <= 1.0:
            raise DetectionError("NMS threshold must be between 0.0 and 1.0.")

        self._confidence_threshold = confidence_threshold
        self._nms_threshold = nms_threshold
        self._labels: list[str] = []
        self._last_nms_explanations: list[str] = []

    def load_labels(self, path: str | Path) -> None:
        """Load class labels.

        Args:
            path: Path to a label file.

        Raises:
            FileNotFoundError: If the label file does not exist.
            DetectionError: If labels cannot be loaded.
        """
        label_path = Path(path)
        if not label_path.exists():
            raise FileNotFoundError(f"Label file not found: {label_path}")
        if not label_path.is_file():
            raise DetectionError(f"Label path is not a file: {label_path}")

        labels = [
            line.strip()
            for line in label_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not labels:
            raise DetectionError(f"Label file is empty: {label_path}")

        self._labels = labels

    def decode(self, raw_output: Any) -> list[Prediction]:
        """Decode raw model output into prediction hypotheses.

        Args:
            raw_output: Raw output returned by the inference engine.

        Returns:
            Prediction hypotheses above the configured confidence threshold,
            sorted by confidence from highest to lowest.

        Raises:
            DetectionError: If labels are missing or the output is unsupported.
        """
        if not self._labels:
            raise DetectionError("Labels must be loaded before decoding predictions.")

        vectors = self._prediction_vectors(raw_output)
        predictions: list[Prediction] = []

        for index, vector in enumerate(vectors):
            if vector.shape[0] < 4 + len(self._labels):
                raise DetectionError(
                    "Prediction vector does not contain enough values for "
                    "box coordinates and class scores."
                )

            box_values = vector[:4]
            class_scores = vector[4 : 4 + len(self._labels)]
            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])

            if confidence < self._confidence_threshold:
                continue

            predictions.append(
                Prediction(
                    index=index,
                    class_id=class_id,
                    label=self._labels[class_id],
                    confidence=confidence,
                    center_x=float(box_values[0]),
                    center_y=float(box_values[1]),
                    width=float(box_values[2]),
                    height=float(box_values[3]),
                )
            )

        return sorted(predictions, key=lambda prediction: prediction.confidence, reverse=True)

    def detect(
        self,
        predictions: list[Prediction],
        metadata: PreprocessingResult,
    ) -> list[Detection]:
        """Convert prediction hypotheses into final detections.

        Args:
            predictions: Ranked prediction hypotheses produced by decode().
            metadata: Preprocessing metadata needed to restore boxes from
                model-input coordinates to original-frame coordinates.

        Returns:
            Final accepted detections.
        """
        self._last_nms_explanations = []
        if not predictions:
            return []

        sorted_predictions = sorted(
            predictions,
            key=lambda prediction: prediction.confidence,
            reverse=True,
        )
        kept_predictions: list[Prediction] = []

        for candidate in sorted_predictions:
            duplicate_of: tuple[Prediction, float] | None = None
            candidate_box = self._prediction_to_model_box(candidate)

            for kept in kept_predictions:
                if candidate.class_id != kept.class_id:
                    continue

                kept_box = self._prediction_to_model_box(kept)
                iou = self._iou(candidate_box, kept_box)
                if iou >= self._nms_threshold:
                    duplicate_of = (kept, iou)
                    break

            if duplicate_of is None:
                kept_predictions.append(candidate)
                continue

            kept, iou = duplicate_of
            self._last_nms_explanations.append(
                "Prediction "
                f"{candidate.index} removed.\n"
                "Reason:\n"
                f"IoU {iou:.2f} with Prediction {kept.index}\n"
                "Confidence lower\n"
                "Prediction discarded."
            )

        return [
            Detection(
                label=prediction.label,
                class_id=prediction.class_id,
                confidence=prediction.confidence,
                box=self._restore_box_to_original(
                    self._prediction_to_model_box(prediction),
                    metadata,
                ),
            )
            for prediction in kept_predictions
        ]

    @property
    def last_nms_explanations(self) -> tuple[str, ...]:
        """Explain which predictions were removed during the last NMS pass."""
        return tuple(self._last_nms_explanations)

    def count_raw_predictions(self, raw_output: Any) -> int:
        """Count raw prediction hypotheses in a model output tensor.

        Args:
            raw_output: Raw output returned by the inference engine.

        Returns:
            Number of raw prediction hypotheses.
        """
        return int(self._prediction_vectors(raw_output).shape[0])

    def _prediction_vectors(self, raw_output: Any) -> np.ndarray:
        """Normalize YOLO output to shape (num_predictions, values_per_prediction)."""
        output = self._first_output_array(raw_output)

        if output.ndim == 0:
            raise DetectionError("YOLO output must not be a scalar.")
        if output.ndim == 1:
            raise DetectionError("YOLO output must contain prediction vectors.")
        if output.ndim == 2:
            return output
        if output.ndim == 3 and output.shape[0] == 1:
            values_per_prediction = 4 + len(self._labels)
            if output.shape[1] == values_per_prediction:
                return np.transpose(output[0], (1, 0))
            if output.shape[2] == values_per_prediction:
                return output[0]

        raise DetectionError(f"Unsupported YOLO output shape: {output.shape}")

    def _first_output_array(self, raw_output: Any) -> np.ndarray:
        """Return the first model output tensor as a NumPy array."""
        if isinstance(raw_output, list | tuple):
            if not raw_output:
                raise DetectionError("Inference produced no output tensors.")
            return np.asarray(raw_output[0])
        return np.asarray(raw_output)

    def _prediction_to_model_box(self, prediction: Prediction) -> tuple[float, float, float, float]:
        """Convert a center-format prediction box to corner coordinates."""
        half_width = prediction.width / 2.0
        half_height = prediction.height / 2.0
        return (
            prediction.center_x - half_width,
            prediction.center_y - half_height,
            prediction.center_x + half_width,
            prediction.center_y + half_height,
        )

    def _iou(
        self,
        first_box: tuple[float, float, float, float],
        second_box: tuple[float, float, float, float],
    ) -> float:
        """Compute intersection over union for two corner-format boxes."""
        first_x1, first_y1, first_x2, first_y2 = first_box
        second_x1, second_y1, second_x2, second_y2 = second_box

        intersection_x1 = max(first_x1, second_x1)
        intersection_y1 = max(first_y1, second_y1)
        intersection_x2 = min(first_x2, second_x2)
        intersection_y2 = min(first_y2, second_y2)

        intersection_width = max(0.0, intersection_x2 - intersection_x1)
        intersection_height = max(0.0, intersection_y2 - intersection_y1)
        intersection_area = intersection_width * intersection_height

        first_area = max(0.0, first_x2 - first_x1) * max(0.0, first_y2 - first_y1)
        second_area = max(0.0, second_x2 - second_x1) * max(0.0, second_y2 - second_y1)
        union_area = first_area + second_area - intersection_area

        if union_area <= 0.0:
            return 0.0
        return intersection_area / union_area

    def _restore_box_to_original(
        self,
        model_box: tuple[float, float, float, float],
        metadata: PreprocessingResult,
    ) -> tuple[int, int, int, int]:
        """Map a model-input box back to original-frame coordinates."""
        if metadata.scale <= 0.0:
            raise DetectionError("Preprocessing scale must be greater than zero.")

        original_height, original_width = metadata.original_shape
        x1, y1, x2, y2 = model_box

        restored_x1 = (x1 - metadata.pad_x) / metadata.scale
        restored_y1 = (y1 - metadata.pad_y) / metadata.scale
        restored_x2 = (x2 - metadata.pad_x) / metadata.scale
        restored_y2 = (y2 - metadata.pad_y) / metadata.scale

        return (
            self._clamp_to_int(restored_x1, 0, original_width),
            self._clamp_to_int(restored_y1, 0, original_height),
            self._clamp_to_int(restored_x2, 0, original_width),
            self._clamp_to_int(restored_y2, 0, original_height),
        )

    def _clamp_to_int(self, value: float, minimum: int, maximum: int) -> int:
        """Round a coordinate and clamp it to image bounds."""
        return max(minimum, min(maximum, int(round(value))))
