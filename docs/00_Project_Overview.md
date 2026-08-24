# 00 Project Overview

## Purpose

GuardianAI v2 is an educational AI vision platform. It teaches students how a computer sees an image, prepares it for a neural network, receives raw model output, converts raw predictions into detections, and then uses those detections in applications.

GuardianAI is not only an object detector. Object detection is the first teaching path.

## Learning Objectives

After using GuardianAI, a student should be able to explain:

- What a camera frame is.
- Why images are converted before entering a model.
- Why neural networks return numerical tensors instead of words.
- How raw predictions become ranked hypotheses.
- Why Non-Maximum Suppression removes duplicate boxes.
- How final detections can power applications.

## Hardware Requirements

Raspberry Pi target:

- Raspberry Pi 4, 4 GB minimum, 8 GB preferred
- Raspberry Pi OS Bookworm or Trixie
- Raspberry Pi Camera Module
- 32 GB or larger microSD card
- Official Raspberry Pi power supply

macOS development:

- macOS
- Python 3
- OpenCV, NumPy, ONNX Runtime
- Static image input

## Software Requirements

Core Python packages:

```text
numpy
opencv-python
onnxruntime
```

Raspberry Pi camera package:

```text
picamera2
```

The Raspberry Pi runtime must not require CUDA, TensorRT, cloud inference, or an NVIDIA GPU.

## Platform Architecture

```text
Physical World
      |
      v
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
      +--> Perception Dashboard
      +--> Guardian Console
      +--> Object Watch
      +--> Guardian Runtime
```

## Current Applications

Perception Dashboard:

- Visualizes the full perception pipeline.
- Shows original image, grayscale, edges, model input, predictions, detections, information, and embedded console state.

Guardian Console:

- Terminal operator console.
- Works over SSH.
- Tracks object presence, confidence, duration, and recent events.

Object Watch:

- Watches for one configurable object.
- Emits events only when the object appears or disappears.

Guardian Runtime:

- Lightweight orchestration layer.
- Selects Learning Mode or Runtime Mode.
- Does not perform inference, detection, rendering, or GPIO.

## Important Commands

Static dashboard:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

Raspberry Pi live dashboard:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Static console:

```bash
python3 -B apps/guardian_console.py --object frisbee --threshold 0.01
```

Object watch:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

## Expected Outputs

Prediction and detection demos commonly show:

```text
Total raw predictions: 8400
Predictions above threshold: 12
Final Detection list
```

The exact confidence values depend on the model, image, and threshold.

## Keyboard Shortcuts

Perception Dashboard:

```text
1-6 highlight stage
p highlight Prediction panel
d highlight Detection panel
space pause/resume
q quit
```

Vision Explorer:

```text
1 original image
2 grayscale
3 blurred image
4 edge detection
5 motion placeholder
6 model input image
d debug information
q quit
```

Terminal applications stop with:

```text
Ctrl+C
```

## Discussion Prompts

- Why does GuardianAI show intermediate stages instead of only final boxes?
- Why does a neural network produce thousands of predictions?
- Why do duplicate predictions happen?
- Why should hardware actions be separate from detection?

## Troubleshooting

If `cv2` is missing:

```bash
python3 -m pip install opencv-python
```

If `onnxruntime` is missing:

```bash
python3 -m pip install onnxruntime
```

If `Picamera2 is required for PiCamera` appears, run the camera app on Raspberry Pi OS with Picamera2 installed.

