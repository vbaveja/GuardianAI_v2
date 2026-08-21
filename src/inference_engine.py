"""Inference engine for ONNX Runtime CPU execution."""

from pathlib import Path
import time
from typing import Any

from src.core.exceptions import InferenceError
from src.types.inference import InferenceResult


class InferenceEngine:
    """Load ONNX models and run CPU inference.

    This module intentionally stops at raw neural network output. It does not
    decode predictions, load labels, perform NMS, or create detections.
    """

    def __init__(self) -> None:
        """Create an unloaded inference engine."""
        self._session: Any | None = None
        self._input_name: str | None = None
        self._model_path: Path | None = None

    def load(self, model_path: str | Path) -> None:
        """Load an ONNX model.

        Args:
            model_path: Path to a deployable ONNX model.

        Raises:
            FileNotFoundError: If the model path does not exist.
            InferenceError: If ONNX Runtime cannot load the model.
        """
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"ONNX model not found: {path}")
        if not path.is_file():
            raise InferenceError(f"ONNX model path is not a file: {path}")

        try:
            import onnxruntime as ort
        except ImportError as error:
            raise InferenceError("onnxruntime is required for inference.") from error

        try:
            session = ort.InferenceSession(
                str(path),
                providers=["CPUExecutionProvider"],
            )
            inputs = session.get_inputs()
        except Exception as error:
            raise InferenceError(f"Unable to load ONNX model: {path}") from error

        if not inputs:
            raise InferenceError(f"ONNX model has no inputs: {path}")

        self._session = session
        self._input_name = inputs[0].name
        self._model_path = path

    def infer(self, tensor: Any) -> InferenceResult:
        """Run inference on a model-ready tensor.

        Args:
            tensor: Preprocessed model input.

        Returns:
            Raw model output and inference timing.

        Raises:
            InferenceError: If no model is loaded or inference fails.
        """
        if self._session is None or self._input_name is None:
            raise InferenceError("InferenceEngine has not loaded a model.")

        try:
            start_time = time.perf_counter()
            raw_output = self._session.run(None, {self._input_name: tensor})
            inference_ms = (time.perf_counter() - start_time) * 1000.0
        except Exception as error:
            raise InferenceError("ONNX inference failed.") from error

        return InferenceResult(raw_output=raw_output, inference_ms=inference_ms)
