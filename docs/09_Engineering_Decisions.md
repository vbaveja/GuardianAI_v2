# 09 Engineering Decisions

## Purpose

This document records the major engineering decisions in GuardianAI v2 so future maintainers understand why the system is shaped this way.

## Decision 1: Education Before Optimization

GuardianAI favors readable code and visible stages.

Reason:

- Students need to understand the pipeline.
- Hidden cleverness makes AI feel magical.

Tradeoff:

- Some algorithms are more verbose than optimized library calls.

## Decision 2: Raspberry Pi First

GuardianAI targets Raspberry Pi.

Required:

- CPU inference
- ONNX Runtime
- Picamera2
- OpenCV
- No CUDA
- No TensorRT
- No cloud inference

Validation command:

```bash
python3 -B apps/perception_dashboard.py --camera --object person --threshold 0.25
```

Expected:

- Camera opens.
- Dashboard updates.
- FPS and inference time appear.

## Decision 3: Camera Abstraction

The `Camera` interface is:

```python
start()
capture()
stop()
```

Implementations:

- `ImageCamera`
- `OpenCVCamera`
- `PiCamera`

Reason:

- The pipeline should not care where frames come from.

## Decision 4: Preprocessor Owns Tensor Conversion

`Preprocessor` owns:

- Frame validation
- Channel normalization
- Letterbox resize
- Pixel normalization
- HWC to CHW
- NCHW batch dimension

It does not own:

- Inference
- Detection
- Labels

Run:

```bash
python3 -B tests/test_preprocessing.py
```

Expected:

```text
Tensor shape: (1, 3, 640, 640)
```

## Decision 5: InferenceEngine Stops At Raw Output

`InferenceEngine` loads ONNX models and runs inference.

It does not decode predictions.

Reason:

- Students should see that neural networks return raw numbers first.

## Decision 6: Prediction Is Separate From Detection

Prediction:

```text
Raw neural-network hypothesis
```

Detection:

```text
Final accepted object after NMS and coordinate restoration
```

Architecture:

```text
raw_output -> decode() -> Prediction -> detect() -> Detection
```

Reason:

- This makes NMS teachable.

## Decision 7: Dashboard Owns Learning Visualization

The Perception Dashboard is an application, not a core AI module.

Reason:

- Visualization is educational.
- But perception logic must remain reusable.

## Decision 8: Guardian Console Uses Simple Terminal Rendering

No curses or external UI framework.

Reason:

- SSH compatibility.
- Simpler classroom setup.

Expected console:

```text
GuardianAI Console
Watching:
Current State:
Current Confidence:
```

## Decision 9: Guardian Runtime Is Single-Threaded

No threads, async, or message buses.

Reason:

- Keep orchestration understandable.
- Avoid concurrency before the architecture needs it.

Tradeoff:

- Multiple applications do not run simultaneously through the runtime.
- The dashboard embeds console state for Learning Mode.

## Troubleshooting Decisions

If performance is slow:

- Measure inference time before optimizing.
- Lower camera resolution only after validating correctness.
- Avoid adding GPU assumptions.

If code feels duplicated:

- Confirm the duplication crosses multiple stable apps.
- Refactor only the reusable piece.

