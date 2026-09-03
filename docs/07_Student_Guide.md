# 07 Student Guide

## What Is GuardianAI?

GuardianAI is a project that helps you learn how a computer sees.

It does not just show the final answer. It shows the steps:

```text
Image -> Tensor -> Neural Network -> Predictions -> Detections -> Application
```

## What You Will Learn

By the end, you should understand:

- A camera image is made of pixels.
- AI models need images in a special format.
- A neural network returns numbers first.
- A prediction is a possible object.
- A detection is a final accepted object.
- Many predictions can describe the same object.
- NMS removes duplicate predictions.

## What You Need

For static image mode:

- A computer with Python 3
- GuardianAI project folder
- OpenCV
- NumPy
- ONNX Runtime

For live camera mode:

- Raspberry Pi 4
- Raspberry Pi Camera Module
- Raspberry Pi OS
- Picamera2

## Start Here

Open a terminal.

On macOS in this workspace:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

On Raspberry Pi:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

## Check The Project

Run:

```bash
ls models/object_detector.onnx labels/coco.txt images/preprocessing_example_original.png
```

Expected:

```text
images/preprocessing_example_original.png
labels/coco.txt
models/object_detector.onnx
```

## Lesson 1: See The Image Processing Steps

Run:

```bash
python3 -B apps/vision_explorer.py
```

An image window should open.

Press:

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

What to notice:

- Grayscale removes color.
- Blur removes small details.
- Edges show outlines.
- Model input shows what the AI actually receives.

Question:

- Which image looks most like what humans see?
- Which image looks most useful for a computer?

## Lesson 2: See The AI Input Tensor

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

What this means:

- Original shape is the starting image size.
- Model image shape is the image size the AI expects.
- Tensor shape is the number format sent into the neural network.
- Padding means black space was added so the image stayed square.

Question:

- Why should we avoid stretching the image?

## Lesson 3: See Raw Neural Network Output

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
Inference time: ...
```

What to notice:

- The AI does not directly say `person`.
- It returns a big tensor of numbers.
- Those numbers must be decoded.

Question:

- Why might an AI model make thousands of guesses?

## Lesson 4: Predictions

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
Prediction index: ...
```

What to notice:

- A prediction is a guess.
- Each prediction has a label, confidence, center, width, and height.
- Low-confidence guesses are removed.

Question:

- Is a prediction the same as a final answer?

Answer:

No. A prediction is only a possible object.

## Lesson 5: Detections

Run:

```bash
python3 -B apps/detection_explorer.py --threshold 0.01
```

Expected output:

```text
IoU means Intersection over Union.
Duplicate predictions occur because YOLO tests many nearby hypotheses.
NMS is required because several hypotheses may describe the same object.

Stage 1
--------
Total raw hypotheses: 8400

Stage 5
--------
Final Detection list
```

What to notice:

- Many predictions may overlap.
- NMS removes duplicate boxes.
- The strongest prediction survives.

Question:

- Why would it be confusing if the AI showed 10 boxes around the same object?

## Lesson 6: Full Dashboard

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

You should see:

```text
Original Image | Grayscale | Edge Detection
Model Input    | Prediction View | Final Detection View
Information Panel
Guardian Console Panel
```

What to notice:

- Prediction View may show many boxes.
- Final Detection View shows fewer boxes.
- The console panel tracks whether the watched object is present.

## Lesson 7: Object Watch

Run:

```bash
python3 -B apps/object_watch.py --object frisbee --threshold 0.01
```

Expected output:

```text
Watching for object: frisbee
Source: images/preprocessing_example_original.png
Press Ctrl+C to stop.

[2026-08-24T12:16:14] PRESENT
Object: frisbee
Confidence: ...
```

Stop:

```text
Ctrl+C
```

What to notice:

- It prints when the object appears.
- It does not repeat the same message every frame.
- It prints again when the object disappears or the program stops.

## Lesson 8: Live Camera On Raspberry Pi

Check camera:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

Expected:

```text
picamera2 ok
```

Run:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected:

- Live camera image appears.
- FPS changes.
- Inference time changes.
- Current state changes when a person appears.

## Important Words

Image:

- A grid of pixels.

Tensor:

- A number array that the neural network can read.

Prediction:

- A possible object guessed by the model.

Detection:

- A final accepted object after duplicate guesses are removed.

IoU:

- A number that measures how much two boxes overlap.

NMS:

- A method that removes duplicate boxes.

## Troubleshooting

If `cv2` is missing:

```bash
python3 -m pip install opencv-python
```

If `onnxruntime` is missing:

```bash
python3 -m pip install onnxruntime
```

If no window appears:

- Click the OpenCV window if it is behind another window.
- If using SSH, try the terminal console:

```bash
python3 -B apps/guardian_console.py --object frisbee --threshold 0.01
```

If camera mode fails:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
```

If no object appears:

- Try a lower threshold:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01 --object frisbee
```

## Final Reflection

Answer these in your own words:

1. What does the neural network output before decoding?
2. Why do we need preprocessing?
3. Why does NMS remove boxes?
4. What is the difference between a prediction and a detection?
5. Why is it useful that GuardianAI can use either an image or a camera?

## Visual Checkpoints

Use these checkpoints to confirm that each lesson is working.

### Vision Explorer

Command:

```bash
python3 -B apps/vision_explorer.py
```

What should I see?

- A window with the image.
- Pressing `1` shows the original image.
- Pressing `2` shows a gray image.
- Pressing `3` shows a smoother blurred image.
- Pressing `4` shows bright lines around edges.
- Pressing `6` shows the exact image shape sent to the neural network.

If your output differs:

- Make sure you ran the command from the project folder.
- Press `d` to print shape, scale, and padding details.
- Press `q` and restart if the window stops responding.

Screenshot placeholder:

```text
[screenshot placeholder: images/vision_explorer_validation.png]
```

### Prediction Explorer

Command:

```bash
python3 -B apps/prediction_explorer.py --threshold 0.01
```

What should I see?

- A line showing thousands of raw predictions.
- A smaller number of predictions above the threshold.
- A top-20 list sorted by confidence.

If your output differs:

- If there are no predictions, lower the threshold to `0.01`.
- If labels look wrong, check that `labels/coco.txt` exists.
- If the model is missing, check `models/object_detector.onnx`.

Screenshot placeholder:

```text
[screenshot placeholder: images/prediction_explorer_validation.png]
```

### Detection Explorer

Command:

```bash
python3 -B apps/detection_explorer.py --threshold 0.01
```

What should I see?

- Predictions before NMS.
- A list of predictions removed because they overlap a stronger prediction.
- A final detection list.

If your output differs:

- If too many boxes survive, the threshold may be too low or the image may contain many objects.
- If no boxes survive, try a clearer image or a lower threshold.
- Read the IoU explanation printed by the app before changing code.

Screenshot placeholder:

```text
[screenshot placeholder: images/detection_explorer_validation.png]
```

### Perception Dashboard

Command:

```bash
python3 -B apps/perception_dashboard.py --threshold 0.01
```

Live Raspberry Pi command:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Perception -> Detection -> Action demo:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
```

What should I see?

- One dashboard window.
- Panels for original image, grayscale, edges, model input, predictions, and detections.
- An information panel with FPS, inference time, prediction count, and detection count.
- An embedded console panel showing watched-object state and recent events.
- With `--sound`, the console shows the action when the watched object appears.

AI perception becomes useful when the machine can respond to what it perceives. In this demo, detecting a person becomes an event, and that event plays `hello.wav` once.

If your output differs:

- If no window opens, check that OpenCV is installed.
- If live camera fails on Raspberry Pi, verify Picamera2 and the camera cable.
- If FPS is low, close other programs and use `htop` to check CPU and memory.

Screenshot:

![Perception Dashboard validation](../images/perception_dashboard_validation.png)

Embedded Console:

![Embedded Console validation](../images/perception_dashboard_validation.png)

Keyboard shortcuts:

- `1`-`6`: Highlight stages.
- `p`: Highlight prediction panel.
- `d`: Highlight detection panel.
- `Space`: Pause or resume live mode.
- `q`: Quit.

## Build Machines Without Code

You can make several GuardianAI machines by changing command-line options.

Person Greeter:

```bash
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once
```

What should I see?

- The app waits for a person.
- When a person appears, it plays the greeting once.
- It waits again after the person leaves.

Garden Guardian:

```bash
python3 -B apps/object_watch.py --camera --object squirrel --sound sounds/hawk.wav --mode continuous --interval 3
```

What should I see?

- The app watches for squirrels.
- While a squirrel stays visible, it plays the sound every 3 seconds.
- It stops playing when the squirrel leaves.

Cat Deterrent:

```bash
python3 -B apps/object_watch.py --camera --object cat --sound sounds/dog.wav --mode continuous --interval 5
```

Bird Monitor:

```bash
python3 -B apps/object_watch.py --camera --object bird --sound sounds/chirp.wav --mode once
```

If your output differs:

- If the sound is missing, the app warns you and keeps watching.
- If no object is detected, try `--threshold 0.10`.
- If the label is wrong, check `labels/coco.txt`.
- If the camera fails, remove `--camera` and test with the static image first.
