# 03 Runtime Guide

## Purpose

Guardian Runtime is a lightweight orchestration layer. It chooses which existing applications to launch. It does not perform inference, detection, rendering, or GPIO.

## Hardware Requirements

Learning Mode on macOS:

- Python 3
- OpenCV
- NumPy
- ONNX Runtime
- Static image

Learning Mode on Raspberry Pi:

- Raspberry Pi 4
- Raspberry Pi Camera Module if using `camera=True`
- Picamera2
- OpenCV
- NumPy
- ONNX Runtime

Runtime Mode on Raspberry Pi:

- Same as above
- GPIO remains placeholder only and is not implemented

## RuntimeConfig

Defined in:

```text
src/guardian_runtime.py
```

Current definition:

```python
RuntimeConfig(
    dashboard=False,
    console=False,
    object_watch=False,
    camera=False,
    target_object="person",
    confidence_threshold=0.25,
    nms_threshold=0.45,
    image_path=Path("images/preprocessing_example_original.png"),
    model_path=Path("models/object_detector.onnx"),
    label_path=Path("labels/coco.txt"),
    interval_seconds=1.0,
)
```

## Architecture

```text
GuardianRuntime
      |
      v
RuntimeConfig
      |
      +-------------------+
      |                   |
      v                   v
Learning Mode        Runtime Mode
      |                   |
      v                   v
Dashboard/Console    Object Watch
```

## Learning Mode

Learning Mode enables educational visibility.

Current preset:

```python
GuardianRuntime.learning_mode(camera=False)
```

Configuration:

```python
RuntimeConfig(
    dashboard=True,
    console=True,
    object_watch=False,
    camera=False,
)
```

Important behavior:

- The runtime is single-threaded.
- It launches enabled modules sequentially.
- Since the dashboard now includes an embedded Guardian Console panel, classroom Learning Mode should normally run the dashboard directly.

Recommended command:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

## Runtime Clarification

Guardian Runtime is intentionally lightweight. It chooses which existing application flow to run; it does not perform inference, detection, rendering, GPIO work, or application business logic itself.

Learning Mode means:

```text
Camera
  |
  v
Perception Dashboard
  |
  v
Embedded Guardian Console panel
```

The dashboard owns the only OpenCV window in Learning Mode. The Guardian Console is displayed as an embedded panel inside that window, not as a second independent interactive application.

Runtime Mode means:

```text
Camera
  |
  v
Object Watch
  |
  v
GPIO placeholder for future deployment behavior
```

Runtime Mode is intended for deployment on the Raspberry Pi where the system watches for a configured object and prints state-change events without rendering a learning dashboard.

Use the dashboard directly for visual classroom learning:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Use runtime mode for deployment-style object watching:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
PY
```

Expected behavior:

- Learning Mode: one dashboard window, live panels, embedded console, keyboard controls.
- Runtime Mode: terminal events only, no dashboard rendering, no GPIO implementation yet.

Troubleshooting:

- If two visual windows appear in Learning Mode, launch `apps/perception_dashboard.py` directly and confirm no separate console process is running.
- If Runtime Mode opens a window, stop the process and verify the runtime path is launching runtime mode, not the dashboard app.

Runtime invocation:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.learning_mode(camera=True).run()
PY
```

Expected behavior:

- The Perception Dashboard launches.
- The embedded console panel shows watched-object state.
- If the dashboard is closed, the runtime may proceed to the next enabled module because execution is sequential.

## Runtime Mode

Runtime Mode is for unattended watching.

Current preset:

```python
GuardianRuntime.runtime_mode(target_object="person", camera=True)
```

Configuration:

```python
RuntimeConfig(
    dashboard=False,
    console=False,
    object_watch=True,
    camera=True,
    target_object="person",
)
```

Run:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
PY
```

Expected output:

```text
Watching for object: person
Source: PiCamera
Press Ctrl+C to stop.
```

When the object appears:

```text
[2026-08-24T12:16:14] PRESENT
Object: person
Confidence: 0.7000
```

When the object disappears:

```text
[2026-08-24T12:16:20] NOT_PRESENT
Total visible duration: 6.02 seconds
Highest confidence observed: 0.9000
```

## GPIO Placeholder

Runtime Mode mentions GPIO as a future placeholder only. No GPIO is implemented.

Current rule:

```text
Detection objects -> Object Watch events -> console output
```

Future rule:

```text
Detection objects -> Scene -> Decision -> ActionEngine -> GPIO
```

## Troubleshooting

Problem:

```text
Picamera2 is required for PiCamera.
```

Cause:

- You ran camera mode on a non-Pi system or Picamera2 is not installed.

Fix:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

or install Picamera2 on Raspberry Pi.

Problem:

```text
ONNX model not found
```

Fix:

```bash
ls models/object_detector.onnx
```

Expected:

```text
models/object_detector.onnx
```

Problem:

Learning Mode does not show dashboard and console simultaneously when launched through `GuardianRuntime`.

Explanation:

- The runtime is intentionally single-threaded.
- Use the Perception Dashboard directly for the integrated learning display:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```
