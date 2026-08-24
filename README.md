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
