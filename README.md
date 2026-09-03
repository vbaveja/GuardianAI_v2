# GuardianAI v2

GuardianAI is an educational embedded AI vision platform for Raspberry Pi. It teaches how images move through a perception pipeline before an application makes decisions.

The current platform can:

- Load frames from a static image or Raspberry Pi camera.
- Preprocess frames into neural-network tensors.
- Run ONNX Runtime CPU inference.
- Decode YOLO predictions.
- Apply Non-Maximum Suppression.
- Display a multi-panel perception dashboard.
- Watch for a target object and emit state-change events.
- Show an SSH-friendly operator console.
- Launch applications through a lightweight Guardian Runtime.

## Hardware Requirements

Minimum Raspberry Pi setup:

- Raspberry Pi 4, 4 GB minimum, 8 GB preferred
- Raspberry Pi OS Bookworm or Trixie
- Raspberry Pi Camera Module
- 32 GB or larger microSD card
- Official Raspberry Pi power supply

Development setup:

- macOS or Raspberry Pi OS
- Python 3.11 recommended for Raspberry Pi
- Git
- OpenCV
- NumPy
- ONNX Runtime
- Picamera2 on Raspberry Pi only

## Quick Start

From the project root:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Expected result:

- One OpenCV window opens.
- The dashboard shows original image, grayscale, edges, model input, predictions, detections, information, and an embedded Guardian Console panel.
- The information panel shows `Raw predictions: 8400`.

Run with Raspberry Pi camera:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Run the visual Perception -> Detection -> Action demo:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
```

## Main Documents

- [Project Overview](docs/00_Project_Overview.md)
- [Quick Start](docs/01_Quick_Start.md)
- [Project Structure](docs/02_Project_Structure.md)
- [Runtime Guide](docs/03_Runtime_Guide.md)
- [Perception Pipeline](docs/04_Perception_Pipeline.md)
- [Applications Guide](docs/05_Applications_Guide.md)
- [Teacher Guide](docs/06_Teacher_Guide.md)
- [Student Guide](docs/07_Student_Guide.md)
- [Extending GuardianAI](docs/08_Extending_GuardianAI.md)
- [Engineering Decisions](docs/09_Engineering_Decisions.md)
- [Troubleshooting](docs/10_Troubleshooting.md)
- [Raspberry Pi Validation](docs/RaspberryPi_Validation.md)
- [API Reference](docs/reference/API_Reference.md)
- [Changelog](docs/CHANGELOG.md)
- [Commands](COMMANDS.md)

## Architecture

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
  +--> Perception Dashboard
  +--> Object Watch
  +--> Guardian Console
```

GuardianAI separates perception from applications. The perception pipeline discovers what is visible. Applications decide how to present or react to that information.

## Screenshot Placeholders

Perception Dashboard and Embedded Guardian Console:

![Perception Dashboard validation](images/perception_dashboard_validation.png)

Additional validation placeholders:

```text
Vision Explorer: images/vision_explorer_validation.png
Prediction Explorer: images/prediction_explorer_validation.png
Detection Explorer: images/detection_explorer_validation.png
```

These placeholders identify expected evidence images for platform validation without requiring a separate screenshot document.

## Quick Start In 10 Minutes

1. Open the project:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

2. Create and activate a virtual environment on Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Confirm model and labels:

```bash
ls models/object_detector.onnx
ls labels/coco.txt
```

4. Run the first visual validation:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

5. Run the configurable Object Watch app:

```bash
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once
```

Expected result:

- The dashboard opens for visual validation.
- Object Watch prints when the object appears and leaves.
- If sound cannot play, GuardianAI prints a warning and continues.

## Complete Onboarding Guide

### macOS Setup

Requirements:

- macOS
- Python 3.10 or newer
- Git
- Static validation image in `images/`
- ONNX model at `models/object_detector.onnx`
- Labels at `labels/coco.txt`

Commands:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Reactivate the virtual environment later:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
source .venv/bin/activate
```

Leave the virtual environment:

```bash
deactivate
```

### Raspberry Pi Setup

Requirements:

- Raspberry Pi 5 recommended, Raspberry Pi 4 acceptable
- Raspberry Pi OS
- Raspberry Pi Camera Module or supported USB camera
- Speaker through USB or 3.5 mm audio for sound applications
- ONNX model at `models/object_detector.onnx`
- Labels at `labels/coco.txt`

Commands:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
python3 --version
python3 -m venv ~/venvs/ai --system-site-packages
source ~/venvs/ai/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -c "from picamera2 import Picamera2; print('Picamera2 OK')"
```

Reactivate the Raspberry Pi virtual environment later:

```bash
source ~/venvs/ai/bin/activate
```

Leave it:

```bash
deactivate
```

### Model And Labels Placement

Expected files:

```bash
mkdir -p models labels sounds images
ls models/object_detector.onnx
ls labels/coco.txt
```

Expected output:

```text
models/object_detector.onnx
labels/coco.txt
```

Place WAV files used by Object Watch in `sounds/`, for example:

```text
sounds/hello.wav
sounds/hawk.wav
sounds/dog.wav
sounds/chirp.wav
```

### First-Run Validation

Run:

```bash
python3 -B tests/test_preprocessing.py
python3 -B apps/inference_explorer.py
python3 -B apps/prediction_explorer.py --threshold 0.01
python3 -B apps/detection_explorer.py --threshold 0.01
python3 -B apps/perception_dashboard.py --threshold 0.01
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once
```

Raspberry Pi live validation:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once
```

### Project Directory Layout

```text
GuardianAI_v2/
  apps/          runnable learning and application programs
  src/           reusable GuardianAI platform modules
  docs/          platform, teacher, student, and maintainer docs
  images/        validation images and screenshots
  labels/        class label files
  models/        ONNX models
  sounds/        WAV files used by sound-based applications
  tests/         validation scripts and tests
```

For failures, start with [Troubleshooting](docs/10_Troubleshooting.md).
