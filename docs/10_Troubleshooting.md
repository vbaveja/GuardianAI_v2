# 10 Troubleshooting

## Purpose

This guide lists common GuardianAI problems and exact fixes.

## Verify Project Location

Run:

```bash
pwd
```

Expected macOS workspace:

```text
/Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

Raspberry Pi example:

```text
/home/pi/Projects/GuardianAI/GuardianAI_v2
```

## Python Version

Run:

```bash
python3 --version
```

Expected Raspberry Pi:

```text
Python 3.11.x
```

## Missing OpenCV

Error:

```text
ModuleNotFoundError: No module named 'cv2'
```

Fix:

```bash
python3 -m pip install opencv-python
```

Verify:

```bash
python3 -B -c "import cv2; print(cv2.__version__)"
```

Expected:

```text
5.x.x
```

or another installed OpenCV version.

## Missing ONNX Runtime

Error:

```text
ModuleNotFoundError: No module named 'onnxruntime'
```

Fix:

```bash
python3 -m pip install onnxruntime
```

Verify:

```bash
python3 -B -c "import onnxruntime; print(onnxruntime.__version__)"
```

Expected:

```text
1.x.x
```

## Missing Picamera2

Error:

```text
Picamera2 is required for PiCamera.
```

Cause:

- Running `--camera` on macOS.
- Picamera2 missing on Raspberry Pi.

Fix:

Run static image mode on macOS:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

On Raspberry Pi, verify:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Expected:

```text
picamera2 ok
```

## Model Missing

Error:

```text
ONNX model not found: models/object_detector.onnx
```

Fix:

```bash
ls models/object_detector.onnx
```

Expected:

```text
models/object_detector.onnx
```

If missing, copy the ONNX model into `models/`.

## Labels Missing

Error:

```text
Label file not found: labels/coco.txt
```

Fix:

```bash
ls labels/coco.txt
```

Expected:

```text
labels/coco.txt
```

## Unsupported YOLO Output Shape

Error:

```text
Unsupported YOLO output shape
```

Cause:

- Model output is not shaped like `(1, 84, N)` or `(1, N, 84)` for COCO.

Inspect:

```bash
python3 -B apps/inference_explorer.py models/object_detector.onnx
```

Expected:

```text
Output tensor shape: (1, 84, 8400)
Number of predictions: 8400
Values per prediction: 84
```

## No Predictions

Output:

```text
Predictions above threshold: 0
```

Try a lower threshold:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

If predictions appear, the model works but the original threshold was too strict for the image.

## No OpenCV Window

Cause:

- Running over SSH without display support.
- Desktop display unavailable.

Use terminal console instead:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

## Camera Does Not Start

Check physical setup:

- Camera cable fully seated.
- Camera enabled in Raspberry Pi OS.
- Adequate power supply.

Run:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected:

- Dashboard opens.
- Source shows `PiCamera`.

## ONNX Runtime Creates :memory:.ses

Observation:

```text
:memory:.ses
```

This can appear during ONNX Runtime validation on macOS.

Cleanup:

```bash
rm ':memory:.ses'
```

## Keyboard Shortcuts Do Not Work

For dashboard:

```text
1-6 highlight stage
p prediction panel
d detection panel
space pause/resume
q quit
```

Click the OpenCV window first, then press the key.

## Expected Validation Sequence

Run:

```bash
python3 -B tests/test_preprocessing.py
python3 -B apps/inference_explorer.py models/object_detector.onnx
python3 -B apps/prediction_explorer.py --threshold 0.01
python3 -B apps/detection_explorer.py --threshold 0.01
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

Expected:

- Preprocessing prints tensor shape.
- Inference prints raw tensor shape.
- Prediction explorer prints ranked predictions.
- Detection explorer prints NMS removals.
- Dashboard opens a visual multi-panel window.

## Object Watch Sound File Missing

Symptom:

```text
Warning: sound file not found: sounds/hello.wav
```

Fix:

- Place the WAV file at the path passed to `--sound`.
- Or choose a different WAV file:

```bash
python3 -B apps/object_watch.py --camera --object person --sound sounds/other.wav --mode once
```

For the Perception Dashboard action demo:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/other.wav
```

The app should continue watching even when the sound is missing.

## aplay Missing

Symptom:

```text
Warning: audio player 'aplay' not found. Sound skipped.
```

Fix on Raspberry Pi:

```bash
sudo apt install alsa-utils
```

macOS note:

- `aplay` is a Linux audio tool. On macOS, this warning is acceptable during validation. The application should keep running.

## Sound Not Audible

Check:

- Confirm the speaker is connected and powered.
- Confirm Raspberry Pi audio output is routed to the expected device.
- Test the WAV directly:

```bash
aplay sounds/hello.wav
```

- Then retry the dashboard demo:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
```

## Object Detected But Action Not Triggered

Check:

- Confirm the dashboard was started with both `--object person` and `--sound sounds/hello.wav`.
- Confirm the embedded console changes from `State: NOT PRESENT` to `State: PRESENT`.
- Move fully out of frame and back in. The action triggers on the appearance transition, not on every visible frame.
- If the object label differs, use the exact label from `labels/coco.txt`.

## Sound Plays Repeatedly Unexpectedly

Expected dashboard behavior:

- The sound plays once when the watched object appears.
- It does not replay while the object remains visible.
- It re-arms only after the object disappears.

If it repeats while the object is still in view:

- Improve lighting or camera position so detection does not flicker between present and not present.
- Lower or raise `--threshold` slightly to stabilize detection.
- Watch the console state. Repeated `NOT PRESENT` to `PRESENT` changes mean the detector is losing and reacquiring the object.

## Wrong Object Label

Symptom:

- The app runs, but the expected object never appears.

Check the label:

```bash
grep -n "^person$" labels/coco.txt
grep -n "^squirrel$" labels/coco.txt
grep -n "^cat$" labels/coco.txt
grep -n "^bird$" labels/coco.txt
```

Fix:

- Use a label that exists in `labels/coco.txt`.
- Match the spelling used by the label file.

## No Detections In Object Watch

Try a lower threshold:

```bash
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once --threshold 0.01
```

For Raspberry Pi camera:

```bash
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once --threshold 0.10
```

Other fixes:

- Improve lighting.
- Move the object closer to the camera.
- Validate the model with `apps/detection_explorer.py`.

## Camera Unavailable In Object Watch

Symptom:

```text
Picamera2 is required for PiCamera.
```

Fix:

- Run camera mode on Raspberry Pi OS with Picamera2 installed.
- Validate without camera first:

```bash
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once --threshold 0.01
```

Then retry live camera:

```bash
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once --threshold 0.25
```
