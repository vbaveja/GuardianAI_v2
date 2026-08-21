"""Camera abstractions for GuardianAI frame sources."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.core.exceptions import CameraError


class Camera(ABC):
    """Abstract interface for GuardianAI frame capture.

    Camera implementations are responsible only for frame acquisition.
    They must not perform preprocessing, inference, detection, or hardware
    actions.
    """

    @abstractmethod
    def start(self) -> None:
        """Start the frame source.

        Raises:
            CameraError: If the frame source cannot be initialized.
        """

    @abstractmethod
    def capture(self) -> Any:
        """Capture one frame.

        Returns:
            Captured image frame from the active source.

        Raises:
            CameraError: If the source is not started or capture fails.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop the frame source and release resources."""


class ImageCamera(Camera):
    """Camera implementation that returns frames from a single image file.

    This source is intended for deterministic testing and development
    workflows where a repeatable frame is more useful than live capture.
    """

    def __init__(self, image_path: str | Path) -> None:
        """Create an image-backed camera.

        Args:
            image_path: Path to the image file used as the frame source.
        """
        self._image_path = Path(image_path)
        self._frame: Any | None = None

    def start(self) -> None:
        """Load the image frame.

        Raises:
            CameraError: If OpenCV is unavailable, the image is missing, or
                the image cannot be decoded.
        """
        if not self._image_path.exists():
            raise CameraError(f"Image file not found: {self._image_path}")

        try:
            import cv2
        except ImportError as error:
            raise CameraError("OpenCV is required for ImageCamera.") from error

        frame = cv2.imread(str(self._image_path))
        if frame is None:
            raise CameraError(f"Unable to read image file: {self._image_path}")

        self._frame = frame

    def capture(self) -> Any:
        """Return a copy of the loaded image frame.

        Returns:
            Captured image frame.

        Raises:
            CameraError: If the image camera has not been started.
        """
        if self._frame is None:
            raise CameraError("ImageCamera has not been started.")

        return self._frame.copy()

    def stop(self) -> None:
        """Release the loaded image frame."""
        self._frame = None


class OpenCVCamera(Camera):
    """Desktop development camera backed by OpenCV video capture.

    This implementation is intended for local workstation testing only.
    Raspberry Pi camera support belongs in PiCamera.
    """

    def __init__(
        self,
        device_index: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        """Create an OpenCV-backed camera.

        Args:
            device_index: OpenCV camera device index.
            width: Optional requested capture width.
            height: Optional requested capture height.
        """
        self._device_index = device_index
        self._width = width
        self._height = height
        self._capture: Any | None = None
        self._cv2: Any | None = None

    def start(self) -> None:
        """Open the configured OpenCV camera device.

        Raises:
            CameraError: If OpenCV is unavailable or the device cannot open.
        """
        try:
            import cv2
        except ImportError as error:
            raise CameraError("OpenCV is required for OpenCVCamera.") from error

        capture = cv2.VideoCapture(self._device_index)
        if not capture.isOpened():
            capture.release()
            raise CameraError(f"Unable to open OpenCV camera: {self._device_index}")

        if self._width is not None:
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        if self._height is not None:
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        self._cv2 = cv2
        self._capture = capture

    def capture(self) -> Any:
        """Capture one frame from the OpenCV device.

        Returns:
            Captured image frame.

        Raises:
            CameraError: If the camera is not started or frame capture fails.
        """
        if self._capture is None:
            raise CameraError("OpenCVCamera has not been started.")

        success, frame = self._capture.read()
        if not success or frame is None:
            raise CameraError("OpenCV camera failed to capture a frame.")

        return frame

    def stop(self) -> None:
        """Release the OpenCV camera device."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._cv2 = None


class PiCamera(Camera):
    """Raspberry Pi camera placeholder for future Picamera2 integration."""

    def start(self) -> None:
        """Start the Raspberry Pi camera.

        Raises:
            CameraError: Always, until Picamera2 support is implemented.
        """
        # TODO: Implement Picamera2 startup for Raspberry Pi hardware.
        raise CameraError("PiCamera is not implemented yet.")

    def capture(self) -> Any:
        """Capture one Raspberry Pi camera frame.

        Returns:
            Captured image frame.

        Raises:
            CameraError: Always, until Picamera2 support is implemented.
        """
        # TODO: Capture a frame using Picamera2.
        raise CameraError("PiCamera is not implemented yet.")

    def stop(self) -> None:
        """Stop the Raspberry Pi camera."""
        # TODO: Release Picamera2 resources.
