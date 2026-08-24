# 02 Project Structure

## Purpose

This document explains where GuardianAI code and assets live. It is written for new developers and maintainers.

## Repository Layout

```text
GuardianAI_v2/
  apps/
  assets/
  docs/
  images/
  labels/
  models/
  notebooks/
  src/
  tests/
  README.md
  COMMANDS.md
```

## apps/

Application entry points live here.

Current applications:

```text
apps/vision_explorer.py
apps/inference_explorer.py
apps/prediction_explorer.py
apps/detection_explorer.py
apps/perception_dashboard.py
apps/object_watch.py
apps/guardian_console.py
```

Applications assemble reusable modules. They may contain application flow and educational display code. They should not duplicate reusable AI logic.

Run an app:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Expected:

```text
OpenCV dashboard window opens
```

## src/

Reusable project modules live here.

```text
src/camera.py
src/preprocessing.py
src/inference_engine.py
src/detector.py
src/guardian_runtime.py
src/core/
src/types/
```

## src/core/

Shared infrastructure:

```text
constants.py
exceptions.py
layer.py
```

`constants.py` contains:

```text
MODEL_SIZE = 640
DEFAULT_CONFIDENCE_THRESHOLD = 0.25
DEFAULT_NMS_THRESHOLD = 0.45
DEFAULT_CAMERA_WIDTH = 1280
DEFAULT_CAMERA_HEIGHT = 720
```

`exceptions.py` contains custom project exceptions such as `CameraError`, `InferenceError`, and `DetectionError`.

`layer.py` defines educational perception layers.

## src/types/

Immutable dataclasses used as module contracts:

```text
Detection
Prediction
PreprocessingResult
InferenceResult
PipelineResult
Decision
ActionResult
```

These types prevent modules from passing unstructured dictionaries.

## images/

Image inputs and generated visual outputs.

Current examples:

```text
images/preprocessing_example_original.png
images/preprocessing_model_image.png
images/perception_dashboard_validation.png
```

Do not place permanent brand assets here. Use `assets/` for that.

## labels/

Class label files.

Current file:

```text
labels/coco.txt
```

The detector loads this file with:

```python
detector.load_labels("labels/coco.txt")
```

## models/

Deployable ONNX models.

Current expected model:

```text
models/object_detector.onnx
```

Training does not happen in this repository. Models should be exported elsewhere and copied here.

## tests/

Small validation scripts and tests.

Current test:

```bash
python3 -B tests/test_preprocessing.py
```

Expected:

```text
Original shape: (360, 640)
Model image shape: (640, 640, 3)
Tensor shape: (1, 3, 640, 640)
```

## Dependency Direction

```text
apps
  |
  v
src modules
  |
  v
src/types and src/core
```

Lower-level modules should not import app modules.

Exception:

- `src/guardian_runtime.py` imports applications lazily because it is an orchestration layer above applications.

## Developer Rules

- Keep reusable logic in `src/`.
- Keep application flow in `apps/`.
- Keep documents in `docs/`.
- Keep models in `models/`.
- Keep labels in `labels/`.
- Do not mix GPIO with perception code.
- Do not make `InferenceEngine` decode predictions.
- Do not make `Detector` run inference.

## Troubleshooting

If imports fail when running a script, run from the project root:

```bash
pwd
```

Expected macOS workspace:

```text
/Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

Then rerun:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

## Documentation Additions

Additional platform documentation lives in:

```text
docs/RaspberryPi_Validation.md
docs/reference/API_Reference.md
```

Purpose:

- `docs/RaspberryPi_Validation.md`: complete Raspberry Pi setup and validation sequence, including live camera checks, dashboard validation, embedded console validation, Object Watch, performance measurement, and common failures.
- `docs/reference/API_Reference.md`: public API reference for reusable modules, dataclasses, and exceptions.

Use these documents when validating a new Raspberry Pi build or when extending GuardianAI with a new module or application.
