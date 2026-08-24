# 01 Quick Start

## Goal

Run GuardianAI for the first time, first with a static image and then, on Raspberry Pi, with a live camera.

## Learning Objectives

You will learn:

- How to run GuardianAI from the command line.
- How to view the perception dashboard.
- How to switch between static image mode and camera mode.
- How to confirm that inference and detection are working.

## Requirements

macOS or Raspberry Pi:

- Python 3
- NumPy
- OpenCV
- ONNX Runtime
- `models/object_detector.onnx`
- `labels/coco.txt`
- `images/preprocessing_example_original.png`

Raspberry Pi camera mode also requires:

- Raspberry Pi Camera Module
- Picamera2

## 1. Open The Project

macOS path used in this workspace:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

Raspberry Pi example path:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

## 2. Check Python

```bash
python3 --version
```

Expected Raspberry Pi output:

```text
Python 3.11.x
```

macOS development may show:

```text
Python 3.12.x
```

## 3. Check Dependencies

```bash
python3 -B -c "import cv2, numpy, onnxruntime; print('dependencies ok')"
```

Expected output:

```text
dependencies ok
```

If it fails on macOS:

```bash
python3 -m pip install numpy opencv-python onnxruntime
```

On Raspberry Pi, prefer installing system camera support through Raspberry Pi OS tools and project packages through the project virtual environment.

## 4. Run Static Dashboard

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

Expected result:

- One OpenCV window appears.
- Six visual panels appear.
- The embedded Guardian Console appears below the information panel.
- The information panel reports a tensor size like `(1, 3, 640, 640)`.
- The information panel reports `Raw predictions: 8400`.

Expected panel layout:

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

## 5. Run Static Guardian Console

```bash
python3 -B apps/guardian_console.py --object frisbee --threshold 0.01
```

Expected screen:

```text
------------------------------------------------------------
GuardianAI Console

Watching: frisbee
Current State: PRESENT
Current Confidence: ...
Highest Confidence: ...
Visible Duration: ...
Inference Time: ...
FPS: ...
```

Stop with:

```text
Ctrl+C
```

## 6. Run Object Watch

```bash
python3 -B apps/object_watch.py --object frisbee --threshold 0.01
```

Expected event output:

```text
Watching for object: frisbee
Source: images/preprocessing_example_original.png
Press Ctrl+C to stop.

[2026-08-24T12:16:14] PRESENT
Object: frisbee
Confidence: ...
```

Because static image mode reuses one image, the object usually remains present until you press `Ctrl+C`.

## 7. Run Live Camera On Raspberry Pi

Confirm Picamera2:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Expected:

```text
picamera2 ok
```

Run dashboard:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Run terminal console over SSH:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

Run object watch:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

## Observations

Ask:

- Does the dashboard show the same pipeline stages for image and camera input?
- Does changing the source require changing the detector code?
- What happens when the threshold is lowered?
- Why does the static image produce repeated frames?

## Troubleshooting

Problem:

```text
ModuleNotFoundError: No module named 'cv2'
```

Fix:

```bash
python3 -m pip install opencv-python
```

Problem:

```text
ModuleNotFoundError: No module named 'onnxruntime'
```

Fix:

```bash
python3 -m pip install onnxruntime
```

Problem:

```text
Picamera2 is required for PiCamera.
```

Fix:

- Run on Raspberry Pi OS.
- Install or enable Picamera2.
- Verify the camera cable and camera interface.

Problem:

```text
ONNX model not found
```

Fix:

Confirm:

```bash
ls models/object_detector.onnx
```

Expected:

```text
models/object_detector.onnx
```

## Complete Installation Guide

This section is self-contained. A new developer, teacher, or student can use only these steps to install GuardianAI and run the first validation sequence.

### macOS Installation

Hardware:

- Mac with Python 3.10 or newer.
- Built-in camera or USB webcam for webcam experiments.
- Static test image in `images/`.
- ONNX object detection model in `models/`.
- COCO label file in `labels/`.

Commands:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install opencv-python numpy onnxruntime
mkdir -p models labels images
ls models/object_detector.onnx
ls labels/coco.txt
```

Expected output:

```text
Python 3.x.x
models/object_detector.onnx
labels/coco.txt
```

If the model or labels are missing, place the trained ONNX model at `models/object_detector.onnx` and the COCO labels at `labels/coco.txt`, one label per line.

First validation sequence:

```bash
python3 -B tests/test_preprocessing.py
python3 -B apps/inference_explorer.py
python3 -B apps/prediction_explorer.py --threshold 0.01
python3 -B apps/detection_explorer.py --threshold 0.01
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Expected observations:

- Preprocessing prints original shape, model image shape, tensor shape, scale, and padding.
- Inference Explorer prints output tensor shape, inference time, min, max, mean, and sample prediction vectors.
- Prediction Explorer prints raw hypotheses and a ranked list above threshold.
- Detection Explorer explains duplicate removals during NMS.
- Perception Dashboard opens one OpenCV window with visual panels.

### Raspberry Pi Installation

Hardware:

- Raspberry Pi 5 recommended, Raspberry Pi 4 acceptable.
- Raspberry Pi Camera Module or supported USB camera.
- Raspberry Pi OS with camera support enabled.
- Monitor, keyboard, and mouse, or SSH access with display support.
- ONNX model at `models/object_detector.onnx`.
- COCO labels at `labels/coco.txt`.

Commands:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
python3 --version
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install opencv-python numpy onnxruntime
mkdir -p models labels images
ls models/object_detector.onnx
ls labels/coco.txt
python3 -c "from picamera2 import Picamera2; print('Picamera2 OK')"
```

Expected output:

```text
models/object_detector.onnx
labels/coco.txt
Picamera2 OK
```

First Raspberry Pi validation:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected observations:

- The dashboard opens.
- Live frames update.
- FPS and inference time appear in the information panel.
- The embedded console panel shows watched-object state.
- Press `Space` to pause or resume.
- Press `Q` to quit.

### Screenshot Placeholders

Perception Dashboard:

![Perception Dashboard validation](../images/perception_dashboard_validation.png)

Embedded Console:

![Embedded Console validation](../images/perception_dashboard_validation.png)

Vision Explorer:

```text
[screenshot placeholder: images/vision_explorer_validation.png]
```

Prediction Explorer:

```text
[screenshot placeholder: images/prediction_explorer_validation.png]
```

Detection Explorer:

```text
[screenshot placeholder: images/detection_explorer_validation.png]
```
