# GuardianAI Changelog

## Sprint 17B - Selectable Detection Models

Purpose:

- Let applications select an ONNX detector and label file from the command line.
- Run the existing Perception Dashboard and Object Watch with the squirrel detector for Garden Guardian demos.
- Keep the change application-scoped without modifying the validated perception modules.

Files Modified:

- `apps/perception_dashboard.py`
- `apps/object_watch.py`
- `README.md`
- `COMMANDS.md`
- `docs/05_Applications_Guide.md`
- `docs/06_Teacher_Guide.md`
- `docs/07_Student_Guide.md`
- `docs/Squirrel_Model.md`
- `docs/10_Troubleshooting.md`
- `docs/CHANGELOG.md`

Behavior Added:

- `--model` and `--labels` are exposed for the Perception Dashboard and Object Watch.
- Defaults remain `models/object_detector.onnx` and `labels/coco.txt`.
- Startup validation checks model path, label path, and whether `--object` exists in the selected labels.
- Non-default model runs print the selected model, labels, and watched object.

Validation Performed:

```bash
python3 -m py_compile apps/perception_dashboard.py apps/object_watch.py
python3 -B apps/perception_dashboard.py --help
python3 -B apps/object_watch.py --help
python3 -B apps/object_watch.py --model models/squirrel_detector.onnx --labels labels/squirrel.txt --object person --threshold 0.25
```

Raspberry Pi validation commands:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
python3 -B apps/perception_dashboard.py --camera --model models/squirrel_detector.onnx --labels labels/squirrel.txt --object squirrel --threshold 0.25 --sound sounds/hawk.wav
python3 -B apps/object_watch.py --camera --model models/squirrel_detector.onnx --labels labels/squirrel.txt --object squirrel --sound sounds/hawk.wav --mode continuous --interval 30 --threshold 0.25
```

Lessons Learned:

- The existing Guardian facade already accepted model and label paths, so the sprint only needed application-level exposure and validation.
- Validating the watched object against the selected labels prevents silent impossible configurations.

## Sprint 17A - Squirrel Detection Model

Purpose:

- Build a squirrel-specific YOLO object detector for future Garden Guardian work.
- Keep the sprint limited to dataset, training, validation, ONNX export, and compatibility analysis.
- Avoid any changes to GuardianAI runtime source code or applications.

Files Created:

- `models/squirrel_detector.onnx`
- `labels/squirrel.txt`
- `docs/Squirrel_Model.md`

Files Modified:

- `.gitignore`
- `docs/CHANGELOG.md`

Behavior Added:

- No GuardianAI application behavior was changed.
- Added a one-class squirrel ONNX detector artifact and label file for future use.

Validation Performed:

```bash
python3 -m venv .venv-training
.venv-training/bin/yolo version
.venv-training/bin/python -c "import torch; print(torch.backends.mps.is_available())"
.venv-training/bin/yolo detect train model=yolov8n.pt data=data/squirrel/data.yaml epochs=30 imgsz=640 batch=8 device=cpu project=training name=squirrel_v1 exist_ok=True patience=10
.venv-training/bin/yolo detect val model=runs/detect/training/squirrel_v1/weights/best.pt data=data/squirrel/data.yaml split=test imgsz=640 device=cpu project=training name=squirrel_v1_test exist_ok=True
.venv-training/bin/yolo detect predict model=runs/detect/training/squirrel_v1/weights/best.pt source=data/squirrel/images/test imgsz=640 conf=0.25 device=cpu project=training name=squirrel_v1_predictions exist_ok=True
.venv-training/bin/yolo export model=runs/detect/training/squirrel_v1/weights/best.pt format=onnx imgsz=640 opset=12 simplify=False nms=False
```

Results:

- Dataset: Open Images V7 `Squirrel` detection subset.
- Train/validation/test images: 500 / 22 / 22.
- Base model: `yolov8n.pt`.
- Training time: 0.628 hours on CPU.
- Best validation metrics: precision 0.966, recall 0.957, mAP50 0.990, mAP50-95 0.782.
- Held-out test metrics: precision 0.870, recall 0.913, mAP50 0.902, mAP50-95 0.659.
- ONNX input: `images [1, 3, 640, 640] tensor(float)`.
- ONNX output: `output0 [1, 5, 8400] tensor(float)`.
- GuardianAI compatibility: YES, with the existing `Preprocessor`, `InferenceEngine`, and `Detector`.

Lessons Learned:

- A one-class YOLO export without embedded NMS can match GuardianAI's existing raw-output detector contract.
- The available Mac environment did not expose PyTorch MPS, so the first experiment was CPU-only.
- Small validation/test splits can look strong but are not a substitute for Garden Guardian field validation.

## Sprint 16 - Perception Dashboard Action Demo

Purpose:

- Show the complete Camera -> Perception -> Detection -> Decision/Event -> Action flow in the visual Perception Dashboard.
- Support ETHOS demo recording where detecting a person plays `hello.wav`.
- Keep the change dashboard-scoped without changing the validated perception platform.

Files Modified:

- `apps/perception_dashboard.py`
- `README.md`
- `COMMANDS.md`
- `docs/05_Applications_Guide.md`
- `docs/06_Teacher_Guide.md`
- `docs/07_Student_Guide.md`
- `docs/10_Troubleshooting.md`
- `docs/CHANGELOG.md`

Behavior Added:

- Added optional `--sound <wav file>` to the Perception Dashboard.
- When `--sound` is provided, the watched object appearance transition plays the WAV once.
- Remaining visible does not replay the sound; disappearing re-arms the trigger.
- The embedded Guardian Console shows watching label, state, confidence, and action status.
- Sound playback warnings are non-fatal, and playback starts without blocking the dashboard loop.

Validation Performed:

```bash
python3 -m py_compile apps/perception_dashboard.py
python3 -B apps/perception_dashboard.py --help
```

Raspberry Pi validation still required:

```bash
aplay sounds/hello.wav
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25 --sound sounds/hello.wav
```

Lessons Learned:

- The dashboard can demonstrate action behavior by reusing the existing watched-object state transition after its single perception pass.
- For visual demos, a simple persistent action status is enough to make the system response visible in recordings.
- Audio failures should be shown as warnings and should not stop the perception display.

## Sprint 15 - Generic Object Watch

Purpose:

- Generalize Person Greeter into a configurable Object Watch application.
- Let students build several intelligent machines by changing command-line options instead of editing Python code.
- Keep `apps/person_greeter.py` as the introductory Hello World application.

Files Added:

- `requirements.txt`
- `docs/CHANGELOG.md`

Files Modified:

- `apps/object_watch.py`
- `README.md`
- `COMMANDS.md`
- `docs/05_Applications_Guide.md`
- `docs/06_Teacher_Guide.md`
- `docs/07_Student_Guide.md`
- `docs/10_Troubleshooting.md`

Validation:

```bash
python3 -m py_compile apps/object_watch.py src/guardian.py apps/person_greeter.py apps/person_greeter_v2.py apps/guardian_console.py src/guardian_runtime.py
python3 -B apps/object_watch.py --help
```

macOS validation:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -B apps/object_watch.py --object person --sound sounds/hello.wav --mode once --threshold 0.01
```

Raspberry Pi validation:

```bash
python3 -m venv ~/venvs/ai --system-site-packages
source ~/venvs/ai/bin/activate
pip install -r requirements.txt
python3 -B apps/object_watch.py --camera --object person --sound sounds/hello.wav --mode once --threshold 0.25
python3 -B apps/object_watch.py --camera --object squirrel --sound sounds/hawk.wav --mode continuous --interval 3
```

Lessons Learned:

- A single application can become many student-built machines when behavior is configured through command-line options.
- `Guardian` provides the right application-facing surface for this sprint: apps can ask what is visible and what just changed without wiring the perception pipeline.
- Sound playback should remain simple and non-fatal. Missing sound files or missing Linux audio tools should not stop perception.
