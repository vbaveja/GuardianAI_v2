# Squirrel Detection Model

## Purpose

Sprint 17A creates a squirrel-specific YOLO object detector for future Garden Guardian work without changing GuardianAI runtime code or applications.

Final artifacts:

- `models/squirrel_detector.onnx`
- `labels/squirrel.txt`

## Dataset

Dataset source: Open Images V7 object-detection dataset, class `Squirrel`.

The preferred Roboflow Universe "Squirrels Only" dataset was inspected as the initial target, but direct public export required a Roboflow API key in this environment. Open Images V7 was used instead because it provides public bounding-box object-detection annotations.

Local dataset layout:

- `data/squirrel/images/train`: 500 images
- `data/squirrel/images/valid`: 22 images
- `data/squirrel/images/test`: 22 images
- `data/squirrel/data.yaml`

Class names:

- `squirrel`

All exported YOLO labels use class id `0`.

## Dataset Sanity Check

Ten random annotated training images were visually inspected before training.

Findings:

- Bounding boxes surrounded squirrels.
- Labels were squirrel-only.
- No obvious corrupt annotations were seen in the inspected sample.
- The sample included small and large squirrels.
- Backgrounds included trees, branches, foliage, logs, rocks, ground, and close-up scenes.

Known dataset concern: the validation and test splits are small, so metrics should be treated as dataset-only indicators, not real-world Garden Guardian performance.

## Base Model

Base model: `yolov8n.pt`

Reason:

- Nano YOLO detector suitable for a first Raspberry Pi-oriented experiment.
- Small model size and moderate CPU inference cost.
- Raw YOLO detection output remains compatible with GuardianAI's existing detector design.

Model summary after training export:

- 72 fused layers
- 3,005,843 parameters
- 8.1 GFLOPs

Input resolution:

- `640 x 640`

## Training Configuration

Environment:

- Separate virtual environment: `.venv-training`
- Python: 3.12.4
- Ultralytics: 8.4.153
- PyTorch: 2.14.0
- Apple Silicon MPS available: `False`
- Training device: CPU

Training command:

```bash
HOME=/private/tmp/guardianai-ultralytics \
YOLO_CONFIG_DIR=/Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2/.ultralytics \
.venv-training/bin/yolo detect train \
  model=yolov8n.pt \
  data=data/squirrel/data.yaml \
  epochs=30 \
  imgsz=640 \
  batch=8 \
  device=cpu \
  project=training \
  name=squirrel_v1 \
  exist_ok=True \
  patience=10
```

Training time:

- 30 epochs completed in 0.628 hours.

Best validation metrics:

- Precision: 0.966
- Recall: 0.957
- mAP50: 0.990
- mAP50-95: 0.782

Final epoch training losses:

- box loss: 0.71482
- class loss: 0.56973
- DFL loss: 1.18169

Held-out test metrics:

- Precision: 0.870
- Recall: 0.913
- mAP50: 0.902
- mAP50-95: 0.659

## Prediction Inspection

Predictions were generated on the 22-image test split and visually inspected.

Observed behavior:

- Squirrels were detected in all rendered test images at `conf=0.25`.
- Boxes were generally reasonable for close-up squirrels, squirrels on branches, squirrels on rocks, squirrels in grass, and multi-squirrel images.
- Some overlapping/duplicate boxes appeared in crowded or partially occluded examples, which GuardianAI's NMS is expected to reduce.

## ONNX Export

Export command:

```bash
HOME=/private/tmp/guardianai-ultralytics \
YOLO_CONFIG_DIR=/Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2/.ultralytics \
.venv-training/bin/yolo export \
  model=runs/detect/training/squirrel_v1/weights/best.pt \
  format=onnx \
  imgsz=640 \
  opset=12 \
  simplify=False \
  nms=False
```

Final model:

- `models/squirrel_detector.onnx`
- Size: 12,238,659 bytes

NMS was not embedded in the ONNX export so GuardianAI's existing `Detector` remains responsible for decoding and NMS.

## ONNX Inspection

ONNX Runtime loaded `models/squirrel_detector.onnx` successfully.

Input:

- name: `images`
- shape: `[1, 3, 640, 640]`
- datatype: `tensor(float)`

Output:

- name: `output0`
- shape: `[1, 5, 8400]`
- datatype: `tensor(float)`

The one-class output is `4 box values + 1 squirrel class score`.

## GuardianAI Compatibility

Compatibility result: YES.

Existing component findings:

- `src/preprocessing.py` produces NCHW float32 input at `640 x 640`, normalized to `0.0-1.0`.
- `src/inference_engine.py` loads ONNX Runtime CPU models and feeds the first input tensor.
- `src/detector.py` supports output shape `(1, values, predictions)` where `values = 4 + len(labels)`.
- With `labels/squirrel.txt`, `values = 5`, so `(1, 5, 8400)` is decoded unchanged.
- The detector expects center-format YOLO boxes followed by class scores, which matches the exported model.
- GuardianAI's existing NMS remains applicable because export used `nms=False`.

Local GuardianAI component test:

```bash
.venv-training/bin/python - <<'PY'
from pathlib import Path
import cv2
from src.preprocessing import Preprocessor
from src.inference_engine import InferenceEngine
from src.detector import Detector

images = sorted(Path("data/squirrel/images/test").glob("*.jpg"))[:5]
preprocessor = Preprocessor()
engine = InferenceEngine()
engine.load("models/squirrel_detector.onnx")
detector = Detector(confidence_threshold=0.25)
detector.load_labels("labels/squirrel.txt")

for image_path in images:
    frame = cv2.imread(str(image_path))
    metadata = preprocessor.process(frame)
    result = engine.infer(metadata.tensor)
    predictions = detector.decode(result.raw_output)
    detections = detector.detect(predictions, metadata)
    top = detections[0] if detections else None
    print(image_path.name, result.inference_ms, top.label if top else None)
PY
```

Mac inference time in that test:

- Approximately 29.6-37.8 ms per image on Apple M3 CPU.

## Raspberry Pi Validation

Observed Sprint 17B Raspberry Pi results:

- ONNX load: successful.
- Output shape: `[1, 5, 8400]`.
- Pi camera inference: approximately 546-585 ms.
- Live Pi-camera test: successful.
- Observed confidence: approximately 0.25-0.37.
- Test target: squirrel photograph displayed on another screen.

This is not yet real outdoor squirrel validation. It confirms the selectable squirrel model can load and run through the live Raspberry Pi camera path, but it does not prove field performance against live squirrels, outdoor lighting, motion, or background clutter.

## Known Limitations

- Training used a small local subset of Open Images rather than the larger preferred Roboflow dataset.
- Validation and test splits are small.
- Metrics do not measure performance on the actual Garden Guardian camera, lighting, squirrel distances, motion blur, or Raspberry Pi CPU.
- Real deployment confidence thresholds may need tuning.

## Future Real-World Validation Plan

- Capture Garden Guardian camera samples with squirrels, birds, leaves, branches, grass, and empty scenes.
- Test false positives and misses under real lighting and motion.
- Measure Raspberry Pi inference time with `models/squirrel_detector.onnx`.
- Tune confidence and NMS thresholds before turning this into a Garden Guardian application sprint.
