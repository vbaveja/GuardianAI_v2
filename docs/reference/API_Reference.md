# GuardianAI API Reference

## Purpose

This reference documents the public GuardianAI interfaces that applications and future modules should use. It is intentionally practical: each entry includes purpose, public API, arguments, returns, example usage, and extension notes.

Run examples from the project root:

```bash
cd /Users/vivekbaveja/Documents/FLOS/GuardianAI/GuardianAI_v2
```

Raspberry Pi example:

```bash
cd ~/Projects/GuardianAI/GuardianAI_v2
```

## Camera

Source: `src/camera.py`

Purpose:

- Abstract interface for all frame sources.
- Lets the perception pipeline use static images, desktop webcams, or Raspberry Pi camera frames through the same API.

Public API:

```python
start() -> None
capture() -> Any
stop() -> None
```

Arguments:

- `start()`: none
- `capture()`: none
- `stop()`: none

Returns:

- `capture()` returns a frame object, normally a NumPy image array.
- `start()` and `stop()` return `None`.

Raises:

- `CameraError` when startup or capture fails.

Example usage:

```python
from src.camera import ImageCamera

camera = ImageCamera("images/preprocessing_example_original.png")
try:
    camera.start()
    frame = camera.capture()
finally:
    camera.stop()
```

Extension notes:

- New camera sources should subclass `Camera`.
- Do not add preprocessing, inference, detection, GPIO, or application logic to camera classes.

## ImageCamera

Purpose:

- Deterministic frame source for testing and lessons.
- Loads one image and returns a copy for each capture.

Constructor:

```python
ImageCamera(image_path: str | Path)
```

Arguments:

- `image_path`: path to an image file.

Returns:

- `capture()` returns a BGR image frame.

Example:

```python
from src.camera import ImageCamera

camera = ImageCamera("images/preprocessing_example_original.png")
camera.start()
frame = camera.capture()
camera.stop()
```

Extension notes:

- Use this for repeatable validation.
- Static image mode is the safest first test before live camera work.

## OpenCVCamera

Purpose:

- Desktop webcam source for development.
- Intended for local workstation testing, not the official Raspberry Pi camera path.

Constructor:

```python
OpenCVCamera(device_index: int = 0, width: int | None = None, height: int | None = None)
```

Arguments:

- `device_index`: OpenCV camera index.
- `width`: optional capture width.
- `height`: optional capture height.

Returns:

- `capture()` returns a BGR image frame.

Example:

```python
from src.camera import OpenCVCamera

camera = OpenCVCamera(device_index=0)
try:
    camera.start()
    frame = camera.capture()
finally:
    camera.stop()
```

Extension notes:

- Keep desktop-only assumptions inside this class.
- Do not use this as the Raspberry Pi camera implementation.

## PiCamera

Purpose:

- Raspberry Pi camera implementation backed by Picamera2.

Constructor:

```python
PiCamera(width: int = 1280, height: int = 720)
```

Arguments:

- `width`: requested frame width.
- `height`: requested frame height.

Returns:

- `capture()` returns a BGR image frame from Picamera2.

Example:

```python
from src.camera import PiCamera

camera = PiCamera()
try:
    camera.start()
    frame = camera.capture()
finally:
    camera.stop()
```

Raspberry Pi validation:

```bash
python3 -B -c "from picamera2 import Picamera2; print('picamera2 ok')"
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Extension notes:

- Keep Picamera2 imports lazy so macOS imports do not fail.
- Always release camera resources in `stop()`.

## Preprocessor

Source: `src/preprocessing.py`

Purpose:

- Convert raw BGR frames into model-ready tensors.

Public API:

```python
Preprocessor().process(frame) -> PreprocessingResult
```

Arguments:

- `frame`: NumPy image array. Grayscale, BGR, and BGRA are supported.

Returns:

- `PreprocessingResult`

Example:

```python
from src.camera import ImageCamera
from src.preprocessing import Preprocessor

camera = ImageCamera("images/preprocessing_example_original.png")
camera.start()
frame = camera.capture()
result = Preprocessor().process(frame)
camera.stop()

print(result.tensor.shape)
print(result.model_image.shape)
```

Expected:

```text
(1, 3, 640, 640)
(640, 640, 3)
```

Extension notes:

- Do not run inference here.
- Do not load labels here.
- Preserve `PreprocessingResult` because Detector coordinate restoration depends on it.

## InferenceEngine

Source: `src/inference_engine.py`

Purpose:

- Load ONNX models and run CPU inference.

Public API:

```python
load(model_path: str | Path) -> None
infer(tensor: Any) -> InferenceResult
```

Arguments:

- `model_path`: path to an ONNX model.
- `tensor`: model-ready tensor from `Preprocessor`.

Returns:

- `InferenceResult(raw_output, inference_ms)`

Example:

```python
from src.inference_engine import InferenceEngine

engine = InferenceEngine()
engine.load("models/object_detector.onnx")
result = engine.infer(preprocessing.tensor)
print(result.inference_ms)
```

Extension notes:

- Do not decode predictions here.
- Do not load labels here.
- Keep CPU provider support for Raspberry Pi.

## Detector

Source: `src/detector.py`

Purpose:

- Convert raw YOLO output into `Prediction` objects.
- Convert predictions into final `Detection` objects using NMS and coordinate restoration.

Constructor:

```python
Detector(confidence_threshold: float = 0.25, nms_threshold: float = 0.45)
```

Public API:

```python
load_labels(path: str | Path) -> None
decode(raw_output: Any) -> list[Prediction]
detect(predictions: list[Prediction], metadata: PreprocessingResult) -> list[Detection]
count_raw_predictions(raw_output: Any) -> int
last_nms_explanations -> tuple[str, ...]
```

Arguments:

- `path`: label file path.
- `raw_output`: raw ONNX model output.
- `predictions`: ranked prediction hypotheses from `decode()`.
- `metadata`: preprocessing metadata used to restore coordinates.

Returns:

- `decode()` returns `list[Prediction]`.
- `detect()` returns `list[Detection]`.
- `count_raw_predictions()` returns `int`.
- `last_nms_explanations` returns text explanations from the last NMS pass.

Example:

```python
from src.detector import Detector

detector = Detector(confidence_threshold=0.25)
detector.load_labels("labels/coco.txt")
predictions = detector.decode(inference.raw_output)
detections = detector.detect(predictions, preprocessing)
```

Extension notes:

- Keep prediction decoding separate from final detection.
- Do not run ONNX inference here.
- Do not add decision or GPIO logic here.

## GuardianRuntime

Source: `src/guardian_runtime.py`

Purpose:

- Launch existing GuardianAI applications from a lightweight orchestration layer.

Public API:

```python
GuardianRuntime(config: RuntimeConfig)
GuardianRuntime.learning_mode(camera: bool = False) -> GuardianRuntime
GuardianRuntime.runtime_mode(target_object: str = "person", camera: bool = True) -> GuardianRuntime
run() -> None
```

Example:

```python
from src.guardian_runtime import GuardianRuntime

GuardianRuntime.runtime_mode(target_object="person", camera=True).run()
```

Extension notes:

- Do not add inference, detection, rendering, or GPIO to the runtime.
- The runtime is intentionally single-threaded.
- Learning Mode should use the Perception Dashboard with the embedded console panel.

## Public Dataclasses

### Detection

Purpose:

- Final accepted object after NMS and coordinate restoration.

Fields:

```python
label: str
class_id: int
confidence: float
box: tuple[int, int, int, int]
```

Example:

```python
Detection(label="person", class_id=0, confidence=0.91, box=(10, 20, 100, 220))
```

### Prediction

Purpose:

- Raw model hypothesis after decoding and confidence filtering.

Fields:

```python
index: int
class_id: int
label: str
confidence: float
center_x: float
center_y: float
width: float
height: float
```

### PreprocessingResult

Purpose:

- Tensor and metadata required by inference and coordinate restoration.

Fields:

```python
tensor: Any
model_image: Any
original_shape: tuple[int, int]
scale: float
pad_x: int
pad_y: int
```

### InferenceResult

Purpose:

- Raw inference output and timing.

Fields:

```python
raw_output: Any
inference_ms: float
```

### PipelineResult

Purpose:

- Immutable result contract for future pipeline coordination.

Fields:

```python
frame: Any
layer: Layer
display_frame: Any
detections: tuple[Detection, ...]
inference: InferenceResult | None
preprocessing: PreprocessingResult | None
```

### Decision

Purpose:

- Hardware-independent decision contract for future reasoning.

Fields:

```python
action: str
reason: str
target: str | None
confidence: float | None
metadata: Mapping[str, Any]
```

### ActionResult

Purpose:

- Future action execution result.

Fields:

```python
success: bool
message: str
executed_actions: tuple[str, ...]
```

### RuntimeConfig

Purpose:

- Selects modules and shared app settings for Guardian Runtime.

Fields:

```python
dashboard: bool
console: bool
object_watch: bool
camera: bool
target_object: str
confidence_threshold: float
nms_threshold: float
image_path: Path
model_path: Path
label_path: Path
interval_seconds: float
```

## Public Exceptions

Source: `src/core/exceptions.py`

```python
GuardianAIError
CameraError
PreprocessingError
InferenceError
DetectionError
PipelineError
DisplayError
KeyboardInputError
DecisionError
ActionEngineError
```

Usage:

```python
from src.core.exceptions import GuardianAIError

try:
    ...
except GuardianAIError as error:
    print(error)
```

Extension notes:

- Raise the most specific exception available.
- Application entry points should catch `GuardianAIError` and print readable diagnostics.

