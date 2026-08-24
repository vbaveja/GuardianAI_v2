# 08 Extending GuardianAI

## Purpose

This guide explains how to extend GuardianAI without breaking the architecture.

## Design Rule

Do not start by editing everything. Find the layer that owns the change.

```text
Camera source change      -> src/camera.py
Image-to-tensor change    -> src/preprocessing.py
Model runtime change      -> src/inference_engine.py
Prediction/detection      -> src/detector.py
Application behavior      -> apps/
Runtime orchestration     -> src/guardian_runtime.py
```

## Hardware Requirements

For development:

- macOS or Raspberry Pi
- Python 3
- OpenCV
- NumPy
- ONNX Runtime

For Raspberry Pi validation:

- Raspberry Pi 4
- Raspberry Pi Camera Module
- Picamera2

## Add A New Watched Object

No code change is required if the object exists in `labels/coco.txt`.

Example:

```bash
python3 -B apps/object_watch.py --camera --object bottle --threshold 0.25
```

Expected:

```text
Watching for object: bottle
Source: PiCamera
Press Ctrl+C to stop.
```

## Add A New Application

Create a new file under:

```text
apps/
```

Recommended flow:

```text
Camera
  |
Preprocessor
  |
InferenceEngine
  |
Detector.decode()
  |
Detector.detect()
  |
Your application logic
```

Do not duplicate:

- Letterbox preprocessing
- ONNX inference
- YOLO tensor interpretation
- NMS

## Add A New Model

Place the model in:

```text
models/
```

Example:

```text
models/bird_detector.onnx
```

Run:

```bash
python3 -B apps/inference_explorer.py models/bird_detector.onnx
```

Expected:

```text
Model name: bird_detector.onnx
Input tensor shape: (1, 3, 640, 640)
Output tensor shape: ...
```

If output shape is not `(1, classes+4, N)` or `(1, N, classes+4)`, update architecture deliberately before using it with `Detector`.

## Add New Labels

Place labels in:

```text
labels/
```

Example:

```text
labels/birds.txt
```

Use:

```bash
python3 -B apps/prediction_explorer.py --model models/bird_detector.onnx --labels labels/birds.txt
```

## Add A Scene Layer

Recommended future architecture:

```text
Detection objects
      |
      v
SceneBuilder
      |
      v
Scene
      |
      v
DecisionEngine
```

Scene should answer:

- What objects are present?
- How many?
- Where are they roughly?
- Which object is primary?

Scene should not answer:

- What hardware should activate?

## Add GPIO Later

GPIO belongs in:

```text
src/action_engine.py
```

Do not add GPIO to:

- `src/detector.py`
- `src/inference_engine.py`
- `src/preprocessing.py`
- `apps/perception_dashboard.py`

Future flow:

```text
Scene -> Decision -> ActionEngine -> GPIO
```

## Testing Extension Work

Run static validation first:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Run target app:

```bash
python3 -B apps/object_watch.py --object person --threshold 0.25
```

Run Raspberry Pi camera validation:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

## Discussion Prompts

- Is this change reusable or application-specific?
- Does it belong in `src/` or `apps/`?
- Does it keep inference separate from detection?
- Does it run on Raspberry Pi without a GPU?

## Troubleshooting

Problem:

```text
Unsupported YOLO output shape
```

Fix:

- Inspect model output:

```bash
python3 -B apps/inference_explorer.py models/your_model.onnx
```

Problem:

The app has copied code from another app.

Fix:

- Move repeated perception logic into a reusable helper only if multiple apps need the same behavior.
- Do not refactor validated modules casually.

## Application Skeleton

Use this shape for a new GuardianAI application:

```python
"""Short description of the GuardianAI application."""

from src.camera import ImageCamera
from src.detector import Detector
from src.inference_engine import InferenceEngine
from src.preprocessing import Preprocessor


def main() -> None:
    camera = ImageCamera("images/example.jpg")
    preprocessor = Preprocessor()
    engine = InferenceEngine()
    detector = Detector()

    camera.start()
    try:
        frame = camera.capture()
        preprocessing = preprocessor.process(frame)
        inference = engine.infer(preprocessing.tensor)
        predictions = detector.decode(inference.raw_output)
        detections = detector.detect(predictions, preprocessing)
        # Application-specific behavior belongs here.
    finally:
        camera.stop()


if __name__ == "__main__":
    main()
```

The application coordinates modules. Reusable modules should not import application code.

## Example Folder Structure

```text
GuardianAI_v2/
  apps/
    garden_guardian.py
    parking_assistant.py
    wildlife_guardian.py
  src/
    camera.py
    preprocessing.py
    inference_engine.py
    detector.py
    guardian_runtime.py
    core/
    types/
  models/
    object_detector.onnx
  labels/
    coco.txt
  images/
    validation images and generated screenshots
  tests/
    test_preprocessing.py
```

## How To Build A New Guardian

1. Choose the object or scene the Guardian should care about.
2. Validate the object label exists in `labels/coco.txt`.
3. Start with `apps/object_watch.py` if the behavior is event-based.
4. Start with `apps/perception_dashboard.py` if the behavior needs visual explanation.
5. Keep new state-machine logic inside the new application until it proves reusable.
6. Add shared abstractions only after two or more applications need the same behavior.

Example command for a bottle watcher:

```bash
python3 -B apps/object_watch.py --camera --object bottle --threshold 0.25
```

Expected output:

```text
2026-08-24T10:15:03 bottle appeared confidence=0.78
2026-08-24T10:15:09 bottle lost duration=6.1s highest_confidence=0.82
```

## Reusing The Perception Pipeline

```text
Camera
  |
  v
Preprocessor
  |
  v
InferenceEngine
  |
  v
Detector.decode()
  |
  v
Prediction objects
  |
  v
Detector.detect()
  |
  v
Detection objects
  |
  v
Application-specific behavior
```

Extension rules:

- Reuse `Camera` implementations instead of opening cameras directly in applications.
- Reuse `Preprocessor` instead of resizing images in applications.
- Reuse `InferenceEngine` instead of calling ONNX Runtime directly.
- Reuse `Detector.decode()` for raw hypotheses.
- Reuse `Detector.detect()` for final accepted objects.
- Add application behavior after detections are produced.

Common mistakes:

- Mixing GPIO behavior into `Detector`.
- Adding application-specific labels inside `InferenceEngine`.
- Creating a second camera inside a dashboard panel.
- Repeating preprocessing logic inside an app.
