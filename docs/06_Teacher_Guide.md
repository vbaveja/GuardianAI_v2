# 06 Teacher Guide

## Lesson Title

GuardianAI: How Images Become AI Detections

## Audience

High school students learning AI, computer vision, robotics, or embedded systems for the first time.

## Lesson Length

Recommended:

- 60 minutes for a static image lesson.
- 90 minutes if using Raspberry Pi camera hardware.

## Learning Objectives

By the end of the lesson, students should be able to:

- Describe the difference between an image, a tensor, a prediction, and a detection.
- Explain why an AI model does not directly return simple words like `person`.
- Explain why one object may produce many predictions.
- Explain what Non-Maximum Suppression does.
- Run GuardianAI commands.
- Observe how the same pipeline works with a static image or live camera.

## Hardware Requirements

Static classroom setup:

- One teacher computer
- Projector or shared screen
- Python 3
- OpenCV
- NumPy
- ONNX Runtime
- GuardianAI repo
- `models/object_detector.onnx`
- `labels/coco.txt`
- `images/preprocessing_example_original.png`

Raspberry Pi classroom setup:

- Raspberry Pi 4, 4 GB minimum
- Raspberry Pi OS Bookworm or Trixie
- Raspberry Pi Camera Module
- Keyboard, monitor, or SSH access
- Official Raspberry Pi power supply
- Same GuardianAI repo and model files

## Setup Before Class

Open the project.

macOS workspace:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

Raspberry Pi example:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

Check dependencies:

```bash
python3 -B -c "import cv2, numpy, onnxruntime; print('dependencies ok')"
```

Expected output:

```text
dependencies ok
```

Check model and labels:

```bash
ls models/object_detector.onnx labels/coco.txt
```

Expected output:

```text
labels/coco.txt
models/object_detector.onnx
```

If using Raspberry Pi camera:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Expected:

```text
picamera2 ok
```

## Lesson Plan

### Part 1: Hook

Ask students:

- When a computer sees a picture, what does it actually receive?
- Does an AI model see the same image that we see?
- If a model detects a person, does it directly output the word `person`?

Expected student ideas:

- It receives pixels.
- It may resize or change the image.
- It probably produces numbers before labels.

Teacher explanation:

GuardianAI shows each step so AI does not feel like magic.

### Part 2: Preprocessing

Run:

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

Show students:

```text
images/preprocessing_example_original.png
images/preprocessing_model_image.png
```

Ask:

- Why did black padding appear?
- Why does the model input need to be square?
- Why do we convert pixel values from `0-255` to `0-1`?

Expected observations:

- The model input image is `640x640`.
- The original image is not stretched.
- Padding preserves object shapes.

### Part 3: Vision Explorer

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

Ask:

- What information disappears in grayscale?
- What does blur remove?
- Why do edges help detect object boundaries?
- Why does motion require more than one frame?

Expected observations:

- Grayscale removes color.
- Blur removes detail.
- Edges highlight boundaries.
- Model input is letterboxed.

### Part 4: Raw Inference

Run:

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
Minimum value: ...
Maximum value: ...
Mean value: ...
Prediction #1: ...
Prediction #100: ...
Prediction #1000: ...
```

Ask:

- Why are there 8400 predictions?
- Why are these numbers not useful yet?
- What would a detector need to do next?

Expected observation:

- The neural network gives many numbers.
- The output is not yet a list of objects.

### Part 5: Predictions

Run:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

Expected output:

```text
The neural network produced thousands of hypotheses.
Each hypothesis predicts where an object may exist.
Each hypothesis also predicts what class it may be.
The confidence score says how strongly the network believes it.
The detector ranks these hypotheses by confidence.
NMS has not yet been applied.

Total raw predictions: 8400
Predictions above threshold: ...
Top 20 predictions:
```

Ask:

- What is the difference between a raw prediction and a final detection?
- Why does the threshold remove many predictions?

Expected observation:

- Lower thresholds show more predictions.
- Predictions may overlap.

### Part 6: Detections and NMS

Run:

```bash
python3 -B apps/detection_explorer.py --threshold 0.01
```

Expected output:

```text
IoU means Intersection over Union.
It measures how much two boxes overlap compared with their total area.
Duplicate predictions occur because YOLO tests many nearby hypotheses.
NMS is required because several hypotheses may describe the same object.
The strongest prediction survives because it has the highest confidence.

Stage 1
--------
Total raw hypotheses: 8400

Stage 4
--------
Predictions removed by NMS: ...
```

Ask:

- Why do duplicate predictions occur?
- Why should the highest-confidence box survive?
- What would happen if NMS did not exist?

Expected observation:

- Many predictions collapse into fewer final detections.

### Part 7: Integrated Dashboard

Run:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

Keyboard:

```text
1-6 highlight stage
p highlight Prediction panel
d highlight Detection panel
space pause/resume
q quit
```

Expected layout:

```text
Original Image | Grayscale | Edge Detection
Model Input    | Prediction View | Final Detection View
Information Panel
Guardian Console Panel
```

Ask:

- Which panel shows what humans see?
- Which panel shows what the neural network sees?
- Which panel shows raw guesses?
- Which panel shows final accepted objects?

### Part 8: Live Raspberry Pi Camera

Run:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected:

- Live camera frames appear.
- FPS updates.
- Inference time updates.
- Console state changes when a person appears or disappears.

Ask:

- Did the pipeline change when the image source changed?
- Why is camera abstraction useful?

## Assessment

Ask students to explain:

1. Image vs tensor.
2. Prediction vs detection.
3. Why NMS removes boxes.
4. Why the Raspberry Pi version uses CPU inference.
5. Why GuardianAI separates perception from action.

## Troubleshooting During Class

No OpenCV window:

```bash
python3 -B apps/guardian_console.py --object frisbee --threshold 0.01
```

No predictions:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

Camera missing:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Model missing:

```bash
ls models/object_detector.onnx
```

Label missing:

```bash
ls labels/coco.txt
```

## Extension Activity

Have students run:

```bash
python3 -B apps/object_watch.py --object frisbee --threshold 0.01
```

Then ask:

- Why does it print only when the object appears?
- Why does it not repeat the same message every frame?
- How would this become a garden guardian or parking assistant?

## Materials Checklist

Hardware:

- One Mac or Raspberry Pi per group, or one instructor machine for demonstration.
- Raspberry Pi 5 recommended for live camera validation.
- Raspberry Pi Camera Module or supported USB webcam for Pi lessons.
- Display, keyboard, and mouse, or SSH access with configured display support.

Software and files:

- Python 3.10 or newer.
- Virtual environment created and activated.
- `opencv-python`, `numpy`, and `onnxruntime` installed.
- Picamera2 available on Raspberry Pi when using `--camera`.
- `models/object_detector.onnx` present.
- `labels/coco.txt` present.
- At least one validation image in `images/`.

Commands to prepare the room:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install opencv-python numpy onnxruntime
ls models/object_detector.onnx
ls labels/coco.txt
```

Raspberry Pi preparation:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python3 -c "from picamera2 import Picamera2; print('Picamera2 OK')"
```

Expected output:

```text
Picamera2 OK
models/object_detector.onnx
labels/coco.txt
```

## Timing

Suggested 75-minute lesson:

- 0-10 minutes: Mission, hardware check, vocabulary.
- 10-20 minutes: Vision Explorer layers.
- 20-35 minutes: Preprocessing and model input.
- 35-50 minutes: Inference and prediction hypotheses.
- 50-65 minutes: NMS and final detections.
- 65-75 minutes: Reflection, troubleshooting, exit questions.

Short 45-minute lesson:

- 0-5 minutes: Goal and setup.
- 5-20 minutes: Dashboard walkthrough.
- 20-35 minutes: Prediction versus detection discussion.
- 35-45 minutes: Student observations and assessment questions.

## Expected Answers

Question: Why does the model input image sometimes have black padding?

Expected answer: The preprocessor preserves the original aspect ratio and pads the remaining space so the model receives the fixed input size it expects.

Question: Why are there many predictions for one visible object?

Expected answer: YOLO predicts many candidate boxes across the image. Several candidates may overlap the same object before NMS removes duplicates.

Question: What does IoU measure?

Expected answer: IoU measures how much two boxes overlap compared with the total area covered by both boxes.

Question: Why does the highest-confidence prediction survive NMS?

Expected answer: When boxes overlap strongly and represent the same class, GuardianAI keeps the strongest hypothesis and removes weaker duplicates.

Question: Why is Object Watch quiet while the object remains visible?

Expected answer: It uses a state machine and only prints events when the state changes from absent to present or present to absent.

## Assessment Rubric

Emerging:

- Can run at least one application with help.
- Can identify original image and model input.
- Needs support explaining prediction versus detection.

Developing:

- Can run the dashboard and describe most panels.
- Can explain confidence threshold and basic NMS behavior.
- Can identify common setup failures from error messages.

Proficient:

- Can trace `Camera -> Preprocessor -> InferenceEngine -> Detector`.
- Can explain why predictions are not final detections.
- Can use Object Watch and interpret appeared/lost events.

Advanced:

- Can propose a new Guardian application without modifying the perception pipeline.
- Can explain how Raspberry Pi constraints affect FPS and inference time.
- Can distinguish learning-mode visualization from deployment-mode runtime behavior.

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

## Teaching Object Watch Machines

Learning objective:

- Students can explain how one application becomes many intelligent machines through configuration.

Teacher demonstration:

```bash
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once
python3 -B apps/object_watch.py --camera --object squirrel --sound sounds/hawk.wav --mode continuous --interval 3
python3 -B apps/object_watch.py --camera --object cat --sound sounds/dog.wav --mode continuous --interval 5
python3 -B apps/object_watch.py --camera --object bird --sound sounds/chirp.wav --mode once
```

Discussion prompts:

- What changed between these machines?
- Which parts of the AI platform stayed the same?
- Why is changing command-line options safer than editing the detector?
- When should sound play once, and when should it repeat?

Expected answers:

- The object label, sound file, mode, and interval changed.
- Camera, preprocessing, inference, detection, and Guardian facade stayed the same.
- Configuration avoids breaking the validated perception pipeline.
- `once` mode is best for greetings and announcements. `continuous` mode is best for deterrents or repeating alerts.
