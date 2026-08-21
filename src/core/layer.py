"""Educational perception layers for GuardianAI."""

from enum import Enum


class Layer(Enum):
    """Educational layers exposed by the GuardianAI vision pipeline."""

    REALITY = 0
    GRAY = 1
    BLUR = 2
    EDGES = 3
    MOTION = 4
    AI_INPUT = 5
    AI_RAW = 6
    DETECTION = 7
    LOCALIZATION = 8
    REASONING = 9
    ACTION = 10
