# Raspberry Pi Validation Guide

## Purpose

This guide validates GuardianAI on Raspberry Pi from environment setup through live camera operation.

## Hardware Requirements

- Raspberry Pi 4, 4 GB minimum, 8 GB preferred
- Raspberry Pi OS Bookworm or Trixie
- Raspberry Pi Camera Module
- Official Raspberry Pi power supply
- 32 GB or larger microSD card
- Network access for installation

## 1. Open The Project

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

Expected:

```bash
pwd
```

```text
/home/pi/Projects/GuardianAI/GuardianAI_v2
```

Your username or path may differ.

## 2. Create Virtual Environment

```bash
python3 -m venv ~/venvs/ai
source ~/venvs/ai/bin/activate
```

Expected prompt:

```text
(ai) pi@raspberrypi:...
```

Check Python:

```bash
python3 --version
```

Expected:

```text
Python 3.11.x
```

## 3. Install Dependencies

```bash
python3 -m pip install --upgrade pip
python3 -m pip install numpy opencv-python onnxruntime pillow
```

Picamera2 is normally installed through Raspberry Pi OS packages. Validate it:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Expected:

```text
picamera2 ok
```

## 4. Validate Model And Labels

```bash
ls models/object_detector.onnx labels/coco.txt
```

Expected:

```text
labels/coco.txt
models/object_detector.onnx
```

Check labels:

```bash
wc -l labels/coco.txt
```

Expected:

```text
80 labels/coco.txt
```

## 5. Static Preprocessing Validation

```bash
python3 -B tests/test_preprocessing.py
```

Expected:

```text
Original shape: (360, 640)
Model image shape: (640, 640, 3)
Tensor shape: (1, 3, 640, 640)
Scale: 1.0
Padding: pad_x=0, pad_y=140
```

## 6. Static Inference Validation

```bash
python3 -B apps/inference_explorer.py models/object_detector.onnx
```

Expected:

```text
Model name: object_detector.onnx
Input tensor shape: (1, 3, 640, 640)
Output tensor shape: (1, 84, 8400)
Number of predictions: 8400
Values per prediction: 84
Tensor dtype: float32
Inference time: ...
```

Expected inference time:

- Raspberry Pi 4 CPU: roughly hundreds of milliseconds to over one second depending on model size and OS load.
- Target platform goal: 1-3 FPS for object detection.

## 7. Camera Validation

Run a GuardianAI camera path:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected:

- OpenCV window opens on the Pi display.
- Source shows `PiCamera`.
- Live FPS updates.
- Inference time updates.
- Detections appear when supported objects are visible.

If running over SSH without a display, use:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

Expected:

```text
GuardianAI Console
Watching: person
Current State:
Current Confidence:
Highest Confidence:
Visible Duration:
Inference Time:
FPS:
```

## 8. Dashboard With Embedded Console

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected layout:

```text
Original Image | Grayscale | Edge Detection
Model Input    | Prediction View | Final Detection View
Information Panel
Guardian Console Panel
```

Keyboard:

```text
1-6 highlight stage
p highlight Prediction panel
d highlight Detection panel
space pause/resume
q quit
```

Expected observations:

- The embedded console state changes to `PRESENT` when the watched object appears.
- It changes back to `NOT_PRESENT` when the object disappears.
- The dashboard remains the only OpenCV window.

## 9. Object Watch Validation

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

Expected:

```text
Watching for object: person
Source: PiCamera
Press Ctrl+C to stop.
```

When a person appears:

```text
[2026-08-24T12:16:14] PRESENT
Object: person
Confidence: ...
```

When the person disappears:

```text
[2026-08-24T12:16:20] NOT_PRESENT
Total visible duration: ...
Highest confidence observed: ...
```

Stop:

```text
Ctrl+C
```

## 10. Performance Measurement

Run:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

Observe:

```text
Inference Time:
FPS:
```

Expected FPS:

```text
1-3 FPS
```

Expected inference time:

```text
300-1000+ ms depending on model and Raspberry Pi load
```

These are educational targets, not hard guarantees.

## 11. htop Monitoring

Open a second terminal:

```bash
htop
```

Watch:

- CPU usage
- Memory usage
- Whether the Pi is overloaded

Expected:

- CPU may be high during inference.
- Memory should remain below 1 GB preferred for the GuardianAI process and related runtime load.

## 12. Common Failures

Failure:

```text
Picamera2 is required for PiCamera.
```

Fix:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Failure:

```text
ONNX model not found
```

Fix:

```bash
ls models/object_detector.onnx
```

Failure:

```text
Predictions above threshold: 0
```

Try:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

Failure:

```text
No OpenCV window
```

Use SSH-friendly console:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

Failure:

```text
Very low FPS
```

Check:

```bash
htop
```

Then try:

- Close other applications.
- Use Guardian Console instead of Dashboard.
- Confirm power supply is adequate.
- Validate that the model is appropriate for Raspberry Pi CPU inference.

