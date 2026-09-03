# GuardianAI Commands

Run all commands from the project root:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

On Raspberry Pi, use the project path where you copied the repo, for example:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

## Environment Check

```bash
python3 --version
```

Expected:

```text
Python 3.11.x
```

macOS development may show Python 3.12 if that is the active local interpreter.

Check required packages:

```bash
python3 -B -c "import cv2, numpy, onnxruntime; print('dependencies ok')"
```

Expected:

```text
dependencies ok
```

On Raspberry Pi, check Picamera2:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Expected:

```text
picamera2 ok
```

## Preprocessing Test

```bash
python3 -B tests/test_preprocessing.py
```

Expected output:

```text
Original shape: (360, 640)
Model image shape: (640, 640, 3)
Tensor shape: (1, 3, 640, 640)
Scale: 1.0
Padding: pad_x=0, pad_y=140
Saved model image: .../images/preprocessing_model_image.png
```

## Vision Explorer

```bash
python3 -B apps/vision_explorer.py
```

Keyboard:

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

Expected result:

- One OpenCV window opens.
- Pressing number keys changes the displayed learning layer.

## Inference Explorer

```bash
python3 -B apps/inference_explorer.py models/object_detector.onnx
```

Expected output pattern:

```text
Model name: object_detector.onnx
Input tensor shape: (1, 3, 640, 640)
Output tensor shape: (1, 84, 8400)
Number of predictions: 8400
Values per prediction: 84
Tensor dtype: float32
Inference time: ...
```

## Prediction Explorer

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

Expected output includes:

```text
Total raw predictions: 8400
Predictions above threshold: 12
Top 20 predictions:
Prediction index: ...
```

## Detection Explorer

```bash
python3 -B apps/detection_explorer.py --threshold 0.01
```

Expected output includes:

```text
Stage 1
--------
Total raw hypotheses: 8400

Stage 4
--------
Predictions removed by NMS: ...

Stage 5
--------
Final Detection list
```

## Perception Dashboard

Static image:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

Raspberry Pi camera:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Raspberry Pi Perception -> Detection -> Action demo:

```bash
python3 -B apps/perception_dashboard.py \
  --camera \
  --object person \
  --threshold 0.25 \
  --sound sounds/hello.wav
```

Keyboard:

```text
1-6 highlight stage
p highlight Prediction panel
d highlight Detection panel
space pause/resume
q quit
```

Hide embedded console:

```bash
python3 -B apps/perception_dashboard.py --hide-console
```

## Object Watch

Static image:

```bash
python3 -B apps/object_watch.py --object frisbee --threshold 0.01
```

Raspberry Pi camera:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

Expected event output:

```text
[2026-08-24T12:16:14] PRESENT
Object: person
Confidence: 0.7000

[2026-08-24T12:16:20] NOT_PRESENT
Total visible duration: 6.02 seconds
Highest confidence observed: 0.9000
```

## Guardian Console

Static image:

```bash
python3 -B apps/guardian_console.py --object frisbee --threshold 0.01
```

Raspberry Pi camera:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

Expected display:

```text
GuardianAI Console

Watching:
Current State:
Current Confidence:
Highest Confidence:
Visible Duration:
Inference Time:
FPS:
```

## Guardian Runtime

Runtime Mode:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
PY
```

Learning Mode:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.learning_mode(camera=True).run()
PY
```

## Complete Operator Cheat Sheet

Run all commands from the project root unless noted:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

Raspberry Pi project root example:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

### Installation

macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install opencv-python numpy onnxruntime
mkdir -p models labels images
ls models/object_detector.onnx
ls labels/coco.txt
```

Raspberry Pi:

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install opencv-python numpy onnxruntime
python3 -c "from picamera2 import Picamera2; print('Picamera2 OK')"
mkdir -p models labels images
ls models/object_detector.onnx
ls labels/coco.txt
```

### Validation

```bash
source .venv/bin/activate
python3 -B tests/test_preprocessing.py
python3 -B apps/vision_explorer.py
python3 -B apps/inference_explorer.py
python3 -B apps/prediction_explorer.py --threshold 0.01
python3 -B apps/detection_explorer.py --threshold 0.01
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Expected results:

- Preprocessing creates a model input image in `images/`.
- Explorers print educational tensor, prediction, and detection information.
- Dashboard opens one OpenCV window.

### Git Workflow

```bash
git status --short
git diff -- docs README.md COMMANDS.md
git add README.md COMMANDS.md docs
git status --short
git commit -m "Document GuardianAI platform"
```

### Mac Workflow

Static image dashboard:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Desktop webcam dashboard:

```bash
python3 -B apps/perception_dashboard.py --camera --threshold 0.25
```

Object watch with a static image:

```bash
python3 -B apps/object_watch.py --object person --threshold 0.25
```

### Pi Workflow

Live dashboard with embedded console:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Deployment-style runtime:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
PY
```

Object Watch directly:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

### Testing

```bash
python3 -B tests/test_preprocessing.py
python3 -B -m pytest
```

If `pytest` is not installed:

```bash
python3 -m pip install pytest
python3 -B -m pytest
```

### Performance

Watch CPU and memory on Raspberry Pi:

```bash
htop
```

Run the live dashboard and observe FPS:

```bash
python3 -B apps/perception_dashboard.py --camera --threshold 0.25
```

Expected Raspberry Pi performance depends on model size, but CPU-only ONNX inference should report stable FPS and inference time without steadily increasing memory usage.

### Cleanup

Stop applications:

```text
Press Q in OpenCV windows.
Press Ctrl+C in terminal-only apps.
```

Inspect generated validation files:

```bash
ls images
find . -name __pycache__ -type d -prune -print
```

## Object Watch Examples

Person Greeter:

```bash
python3 -B apps/object_watch.py \
  --camera \
  --object person \
  --sound sounds/hello.wav \
  --mode once
```

Garden Guardian:

```bash
python3 -B apps/object_watch.py \
  --camera \
  --object squirrel \
  --sound sounds/hawk.wav \
  --mode continuous \
  --interval 3
```

Cat Deterrent:

```bash
python3 -B apps/object_watch.py \
  --camera \
  --object cat \
  --sound sounds/dog.wav \
  --mode continuous \
  --interval 5
```

Bird Monitor:

```bash
python3 -B apps/object_watch.py \
  --camera \
  --object bird \
  --sound sounds/chirp.wav \
  --mode once
```

Static image validation without Raspberry Pi camera:

```bash
python3 -B apps/object_watch.py \
  --object person \
  --sound sounds/hello.wav \
  --mode once \
  --threshold 0.01
```

Mode behavior:

- `--mode once`: play once per appearance event, stay quiet while visible, re-arm after the object leaves.
- `--mode continuous`: play while visible, wait `--interval` seconds between plays, stop as soon as the object leaves.
