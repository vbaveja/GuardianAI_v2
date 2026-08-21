"""Image preprocessing for preparing frames for neural network inference."""

from typing import Any

import cv2
import numpy as np

from src.core.constants import MODEL_SIZE
from src.core.exceptions import PreprocessingError
from src.types.preprocessing import PreprocessingResult


class Preprocessor:
    """Convert raw image frames into model-ready tensors.

    The preprocessor is the boundary between camera images and neural network
    input. It does not run inference or decode predictions.
    """

    def process(self, frame: Any) -> PreprocessingResult:
        """Preprocess a camera frame.

        Args:
            frame: Original camera frame.

        Returns:
            Model tensor, model image, and coordinate recovery metadata.

        Raises:
            PreprocessingError: If the input frame is missing or malformed.
        """
        bgr_frame = self._validate_and_normalize_channels(frame)
        original_shape = bgr_frame.shape[:2]

        model_image, scale, pad_x, pad_y = self._letterbox(bgr_frame)

        # Neural networks operate on numbers, not image files. Dividing by
        # 255.0 maps standard image pixels from 0-255 into the 0.0-1.0 range.
        normalized = model_image.astype(np.float32) / 255.0

        # Cameras and OpenCV use HWC layout: height, width, channels.
        # Most neural network models expect CHW: channels, height, width.
        chw_tensor = np.transpose(normalized, (2, 0, 1))

        # ONNX models usually receive a batch of images. NCHW adds a batch
        # dimension of 1 around the single image tensor.
        nchw_tensor = np.expand_dims(chw_tensor, axis=0)

        return PreprocessingResult(
            tensor=nchw_tensor,
            model_image=model_image,
            original_shape=original_shape,
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )

    def _validate_and_normalize_channels(self, frame: Any) -> np.ndarray:
        """Validate an input frame and convert it to BGR channel order."""
        if frame is None:
            raise PreprocessingError("Input frame is None.")

        if not isinstance(frame, np.ndarray):
            raise PreprocessingError("Input frame must be a NumPy array.")

        if frame.size == 0:
            raise PreprocessingError("Input frame is empty.")

        if frame.ndim == 2:
            # Grayscale frames have brightness only. Convert them to BGR so the
            # rest of the pipeline can assume three channels.
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        if frame.ndim != 3:
            raise PreprocessingError("Input frame must have 2 or 3 dimensions.")

        channel_count = frame.shape[2]
        if channel_count == 3:
            # OpenCV camera and image reads are already BGR.
            return frame

        if channel_count == 4:
            # BGRA includes an alpha channel for transparency. The neural
            # network sees color, so drop alpha and keep BGR.
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        raise PreprocessingError(
            f"Unsupported channel count: {channel_count}. Expected 1, 3, or 4."
        )

    def _letterbox(self, frame: np.ndarray) -> tuple[np.ndarray, float, int, int]:
        """Resize an image to model size without stretching it."""
        original_height, original_width = frame.shape[:2]
        if original_height <= 0 or original_width <= 0:
            raise PreprocessingError("Input frame has invalid dimensions.")

        # Letterboxing preserves the original shape of objects. Stretching an
        # image could make a circle look like an oval and confuse the model.
        scale = min(MODEL_SIZE / original_width, MODEL_SIZE / original_height)
        resized_width = int(round(original_width * scale))
        resized_height = int(round(original_height * scale))

        resized = cv2.resize(
            frame,
            (resized_width, resized_height),
            interpolation=cv2.INTER_LINEAR,
        )

        # The neural network expects a fixed square input. Black padding fills
        # the unused area after aspect-ratio preserving resize.
        model_image = np.zeros((MODEL_SIZE, MODEL_SIZE, 3), dtype=frame.dtype)
        pad_x = (MODEL_SIZE - resized_width) // 2
        pad_y = (MODEL_SIZE - resized_height) // 2

        model_image[
            pad_y : pad_y + resized_height,
            pad_x : pad_x + resized_width,
        ] = resized

        return model_image, scale, pad_x, pad_y
