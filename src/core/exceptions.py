"""Custom exceptions used across GuardianAI."""


class GuardianAIError(Exception):
    """Base exception for GuardianAI errors."""


class CameraError(GuardianAIError):
    """Raised when camera initialization or capture fails."""


class PreprocessingError(GuardianAIError):
    """Raised when frame preprocessing fails."""


class InferenceError(GuardianAIError):
    """Raised when model loading or inference fails."""


class DetectionError(GuardianAIError):
    """Raised when detection decoding fails."""


class PipelineError(GuardianAIError):
    """Raised when the vision pipeline fails."""


class DisplayError(GuardianAIError):
    """Raised when visualization fails."""


class KeyboardInputError(GuardianAIError):
    """Raised when keyboard input handling fails."""


class DecisionError(GuardianAIError):
    """Raised when decision evaluation fails."""


class ActionEngineError(GuardianAIError):
    """Raised when action execution fails."""
