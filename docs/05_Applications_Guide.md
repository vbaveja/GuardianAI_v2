# 05 Applications Guide

## Purpose

This guide documents the GuardianAI applications. Each application reuses the perception modules instead of duplicating AI logic.

## Hardware Requirements

Static image applications:

- macOS or Raspberry Pi
- Python 3
- OpenCV
- NumPy
- ONNX Runtime

Live camera applications:

- Raspberry Pi 4
- Raspberry Pi Camera Module
- Picamera2

## Shared Files

Required model:

```text
models/object_detector.onnx
```

Required labels:

```text
labels/coco.txt
```

Default image:

```text
images/preprocessing_example_original.png
```

## Vision Explorer

Purpose:

- Explore early image processing stages.
- No inference.
- No detection.

Run:

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

Expected observation:

- The displayed image changes as you press number keys.
- Pressing `6` shows the exact letterboxed image sent into the model.

## Inference Explorer

Purpose:

- Show raw neural-network output before decoding.

Run:

```bash
python3 -B apps/inference_explorer.py models/object_detector.onnx
```

Expected output:

```text
Model name: object_detector.onnx
Input tensor shape: (1, 3, 640, 640)
Output tensor shape: (1, 84, 8400)
Number of predictions: 8400
Values per prediction: 84
Tensor dtype: float32
```

Discussion prompt:

- Why is the output a tensor instead of object names?

## Prediction Explorer

Purpose:

- Convert raw tensor output into ranked prediction hypotheses.
- Stop before NMS.

Run:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

Expected output:

```text
The neural network produced thousands of hypotheses.
Total raw predictions: 8400
Predictions above threshold: ...
Top 20 predictions:
```

## Detection Explorer

Purpose:

- Show how predictions collapse into final detections through NMS.

Run:

```bash
python3 -B apps/detection_explorer.py --threshold 0.01
```

Expected output:

```text
Stage 1
--------
Total raw hypotheses: 8400

Stage 5
--------
Final Detection list
```

## Perception Dashboard

Purpose:

- Integrated visual learning dashboard.
- Shows all major perception stages at once.
- Includes optional embedded Guardian Console panel.

Run static image mode:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

Run live camera mode:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Keyboard:

```text
1-6 highlight stage
p highlight Prediction panel
d highlight Detection panel
space pause/resume
q quit
```

Hide console panel:

```bash
python3 -B apps/perception_dashboard.py --hide-console
```

Expected layout:

```text
Original Image | Grayscale | Edge Detection
Model Input    | Prediction View | Final Detection View
Information Panel
Guardian Console Panel
```

## Guardian Console

Purpose:

- Operator console for SSH.
- No OpenCV window.
- Refreshes terminal in place.

Run static mode:

```bash
python3 -B apps/guardian_console.py --object frisbee --threshold 0.01
```

Run live camera mode:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

Expected display:

```text
GuardianAI Console

Watching: person
Current State: NOT_PRESENT
Current Confidence: n/a
Highest Confidence: n/a
Visible Duration: 0.00s
Inference Time: ...
FPS: ...
```

Stop:

```text
Ctrl+C
```

## Object Watch

Purpose:

- First real GuardianAI application.
- Watches for one object.
- Emits events only when state changes.

Run static:

```bash
python3 -B apps/object_watch.py --object frisbee --threshold 0.01
```

Run live:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

Expected output:

```text
Watching for object: person
Source: PiCamera
Press Ctrl+C to stop.

[2026-08-24T12:16:14] PRESENT
Object: person
Confidence: 0.7000
```

## Guardian Runtime

Purpose:

- Lightweight application launcher.
- Does not perform inference or detection.

Run Runtime Mode:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
PY
```

Run Learning Mode:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.learning_mode(camera=True).run()
PY
```

Recommendation:

- Use `apps/perception_dashboard.py` directly for classroom Learning Mode because it includes the embedded console panel in one OpenCV window.

## Troubleshooting

If an OpenCV window does not appear:

- Confirm you are not using SSH without display forwarding.
- Use Guardian Console instead:

```bash
python3 -B apps/guardian_console.py --camera --object person --threshold 0.25
```

If object events do not appear:

- Lower threshold:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.10
```

- Confirm the object label exists:

```bash
grep -n "^person$" labels/coco.txt
```

## Screenshot Placeholders

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

## Expanded Application Reference

### Vision Explorer

Purpose:

- Shows how an image changes through basic computer vision layers before neural-network inference.

Command:

```bash
python3 -B apps/vision_explorer.py
```

CLI options:

- Uses the configured default static image.

Example output:

```text
Original shape: (480, 640, 3)
Model image shape: (640, 640, 3)
Tensor shape: (1, 3, 640, 640)
Scale: 1.0
Padding: x=0, y=80
```

Expected behavior:

- One OpenCV window opens.
- Keys switch between original, grayscale, blur, edges, motion placeholder, and model input.

Keyboard shortcuts:

- `1`: Original image
- `2`: Grayscale
- `3`: Blurred image
- `4`: Edge detection
- `5`: Motion placeholder
- `6`: Model input image
- `d`: Print debug information
- `q`: Quit

Common mistakes:

- Running from the wrong directory, causing image paths to fail.
- Expecting detections; this app intentionally does not run inference or detection.

### Inference Explorer

Purpose:

- Shows raw neural-network tensor output before labels, decoding, NMS, or detections.

Command:

```bash
python3 -B apps/inference_explorer.py
```

CLI options:

- Uses the configured static image and model path.

Example output:

```text
Model name: object_detector.onnx
Input tensor shape: (1, 3, 640, 640)
Output tensor shape: (1, 84, 8400)
Number of predictions: 8400
Values per prediction: 84
Inference time: 120.4 ms
```

Expected behavior:

- Original image displays.
- Console prints raw tensor statistics and sample prediction vectors.

Keyboard shortcuts:

- `q`: Quit the image window.

Common mistakes:

- Expecting class names; this app intentionally does not load labels or decode predictions.

### Prediction Explorer

Purpose:

- Converts raw model output into ranked `Prediction` hypotheses.

Command:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

CLI options:

- `--threshold <confidence>`: minimum confidence for keeping a prediction.

Example output:

```text
Total raw predictions: 8400
Predictions above threshold: 12
Top 20 predictions:
Prediction index: 8214 | Label: frisbee | Confidence: 0.1653
```

Expected behavior:

- Console shows candidate predictions sorted by confidence.
- Duplicate predictions may still appear because NMS has not run.

Keyboard shortcuts:

- None; this is a console learning app.

Common mistakes:

- Using too high a threshold for early experiments. Try `--threshold 0.01`.
- Treating predictions as final detections. They are hypotheses only.

### Detection Explorer

Purpose:

- Demonstrates how predictions become final detections through IoU and NMS.

Command:

```bash
python3 -B apps/detection_explorer.py --threshold 0.01
```

CLI options:

- `--threshold <confidence>`: minimum prediction confidence.

Example output:

```text
Prediction 8191 removed.
Reason:
IoU 0.84 with Prediction 8189
Confidence lower
Prediction discarded.
```

Expected behavior:

- Console explains which duplicate boxes were removed and why.
- Final detection list is shorter than the prediction list.

Keyboard shortcuts:

- None; this is a console learning app.

Common mistakes:

- Expecting every high-confidence prediction to survive. NMS removes overlapping duplicates.

### Perception Dashboard

Purpose:

- Combines the visual learning stages into one dashboard.
- Optionally demonstrates an action when the watched object appears.

Command:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Live Raspberry Pi command:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Live Perception -> Detection -> Action demo:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
```

CLI options:

- `--camera`: use live camera instead of static image.
- `--object <label>`: watched object for embedded console panel.
- `--threshold <confidence>`: confidence threshold.
- `--sound <wav file>`: optional WAV file to play once when the watched object appears.

Example output:

```text
GuardianAI Perception Dashboard
FPS: 4.8
Inference time: 118.7 ms
Predictions after threshold: 12
Predictions after NMS: 1
```

Expected behavior:

- One OpenCV window shows original image, grayscale, edges, model input, predictions, detections, and information.
- Embedded console panel updates inside the same window.

Keyboard shortcuts:

- `1`-`6`: Highlight a processing stage.
- `p`: Highlight Prediction panel.
- `d`: Highlight Detection panel.
- `Space`: Advance, pause, or resume depending on mode.
- `q`: Quit.

Common mistakes:

- Starting Guardian Console separately during Learning Mode. The dashboard already embeds the console panel.

### Guardian Console

Purpose:

- Shows Object Watch state in a terminal display for SSH-friendly operation.

Command:

```bash
python3 -B apps/guardian_console.py --object person --threshold 0.25
```

CLI options:

- `--camera`: use live camera.
- `--object <label>`: watched object.
- `--threshold <confidence>`: detection confidence threshold.

Example output:

```text
GuardianAI Console
Watching: person
Current State: PRESENT
Current Confidence: 0.82
Highest Confidence: 0.91
Visible Duration: 00:00:07
Inference Time: 119.8 ms
FPS: 4.9
```

Expected behavior:

- The terminal refreshes in place.
- Recent events show appearances and losses.

Keyboard shortcuts:

- `Ctrl+C`: Quit.

Common mistakes:

- Expecting a visual dashboard. This app is terminal-only.

### Object Watch

Purpose:

- Watches for one configured object and prints events only when state changes.

Command:

```bash
python3 -B apps/object_watch.py --object person --threshold 0.25
```

Live Raspberry Pi command:

```bash
python3 -B apps/object_watch.py --camera --object person --threshold 0.25
```

CLI options:

- `--camera`: use live camera.
- `--object <label>`: object label to watch.
- `--threshold <confidence>`: detection confidence threshold.

Example output:

```text
2026-08-24T10:15:03 person appeared confidence=0.84
2026-08-24T10:15:11 person lost duration=8.2s highest_confidence=0.91
```

Expected behavior:

- Appeared event prints once when the object enters.
- No repeated announcements while the object remains visible.
- Lost event prints when the object disappears.

Keyboard shortcuts:

- `Ctrl+C`: Quit.

Common mistakes:

- Using a label that is not in `labels/coco.txt`.

### Guardian Runtime

Purpose:

- Selects either Learning Mode or Runtime Mode without owning perception logic.

Learning command:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.learning_mode(camera=True).run()
PY
```

Runtime command:

```bash
python3 -B - <<'PY'
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
PY
```

CLI options:

- Guardian Runtime is primarily used as a Python orchestration API in the current platform.
- Runtime configuration chooses dashboard, embedded console, object watch, and camera behavior.

Example output:

```text
Starting GuardianAI Runtime
Mode: runtime
Object Watch enabled
GPIO placeholder disabled
```

Expected behavior:

- Learning Mode opens one dashboard window with embedded console.
- Runtime Mode prints object watch events and avoids rendering.

Keyboard shortcuts:

- Learning Mode: same as Perception Dashboard.
- Runtime Mode: `Ctrl+C`.

Common mistakes:

- Assuming runtime performs AI logic. It only coordinates existing application flows.

## Sprint 15 Object Watch

Purpose:

- Lets students build multiple intelligent machines by changing command-line options instead of editing Python code.
- Reuses `Guardian`, which composes the existing perception platform.

CLI options:

- `--camera`: use Raspberry Pi camera.
- `--object <label>`: object to watch, default `person`.
- `--sound <wav file>`: WAV file to play.
- `--threshold <float>`: detection confidence threshold, default `0.25`.
- `--mode once|continuous`: sound behavior, default `once`.
- `--interval <seconds>`: delay between plays in continuous mode, default `3`.

Example commands:

```bash
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once
python3 -B apps/object_watch.py --camera --object squirrel --sound sounds/hawk.wav --mode continuous --interval 3
python3 -B apps/object_watch.py --camera --object cat --sound sounds/dog.wav --mode continuous --interval 5
python3 -B apps/object_watch.py --camera --object bird --sound sounds/chirp.wav --mode once
```

Expected output:

```text
Watching for object: person
Mode: once
Sound: sounds/hello.wav
Source: PiCamera
Press Ctrl+C to stop.

Waiting for person...
Person detected.
Playing sound...
Person still visible.
Person left.
Waiting again...
```

Validation:

```bash
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once --threshold 0.01
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once --threshold 0.25
```

Troubleshooting:

- Missing sound file: the app prints a warning and keeps watching.
- `aplay` missing: install ALSA utilities on Raspberry Pi or continue without sound.
- Wrong object label: confirm the label exists in `labels/coco.txt`.
- No detections: lower `--threshold`, improve lighting, or use a clearer test object.
- Camera unavailable: run without `--camera` to validate the rest of the app with a static image.
