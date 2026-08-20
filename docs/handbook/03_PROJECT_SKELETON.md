# GuardianAI Engineering Handbook

# Chapter 3 — Project Skeleton

**Version:** 1.0 (Draft)

---

# 1. Purpose

This document defines the physical organization of the GuardianAI_v2
repository.

Architecture explains **how the system works**.

The Project Skeleton explains **where every piece of code belongs**.

Its objectives are:

- Keep the repository easy to understand.
- Make every file have one responsibility.
- Provide a consistent structure for future contributors.
- Allow Codex to implement features without reorganizing the project.

---

# 2. Repository Philosophy

GuardianAI follows five organizational rules.

1. Every directory has one clear purpose.
2. Every module has one responsibility.
3. Reusable code belongs in `src/`.
4. User-facing applications belong in `apps/`.
5. Documentation evolves with the software.

---

# 3. Repository Layout

```
GuardianAI/
├── GuardianAI_v1/
└── GuardianAI_v2/
    ├── docs/
    ├── src/
    ├── apps/
    ├── models/
    ├── labels/
    ├── images/
    ├── assets/
    ├── notebooks/
    ├── tests/
    ├── requirements.txt
    └── README.md
```

GuardianAI_v1 is the Computer Vision learning path.

GuardianAI_v2 is the production-quality AI Vision platform.

---

# 4. Directory Responsibilities

## docs/

Contains all engineering documentation.

Examples:

- 01_VISION.md
- 02_ARCHITECTURE.md
- 03_PROJECT_SKELETON.md
- 04_TARGET_PLATFORM.md
- 05_ENGINEERING_WORKFLOW.md
- 06_CODE_GUIDELINES.md
- 07_DESIGN_PHILOSOPHY.md
- 08_ROADMAP.md
- 09_CURRICULUM.md

No source code belongs here.

---

## src/

Contains reusable modules.

Applications must consume these modules rather than duplicating logic.

Core modules:

camera.py

preprocessing.py

ai_engine.py

detector.py

vision_pipeline.py

display.py

keyboard.py

decision_engine.py

action_engine.py

future:
audio_engine.py
gps_engine.py
sdr_engine.py

---

## apps/

Contains executable applications.

Each application assembles reusable modules into a solution.

Examples

guardian_ai.py

vision_explorer.py

garden_guardian.py

parking_assistant.py

face_guardian.py

Applications should contain almost no AI logic.

They coordinate reusable modules.

---

## models/

Stores deployable AI models.

Examples

object_detector.onnx

face_detector.onnx

bird_detector.onnx

Training never occurs inside this repository.

---

## labels/

Stores class labels.

Examples

coco.txt

birds.txt

faces.txt

---

## images/

Contains

Input images

Captured frames

Annotated output

Example datasets

No permanent assets.

---

## assets/

Contains

Icons

Logos

Documentation figures

User-interface graphics

---

## notebooks/

Purpose

Rapid experimentation.

Acceptable:

Benchmarking

Algorithm exploration

Performance analysis

Not acceptable:

Production code

---

## tests/

Every reusable module should have a matching test.

Example

camera.py
→ test_camera.py

preprocessing.py
→ test_preprocessing.py

detector.py
→ test_detector.py

vision_pipeline.py
→ test_pipeline.py

---

# 5. Source Module Responsibilities

camera.py

Owns camera lifecycle.

Public interface

start()

capture()

stop()

---

preprocessing.py

Owns

Resize

Letterbox

Normalization

Tensor conversion

Never performs inference.

---

ai_engine.py

Owns

Model loading

Inference

Session lifecycle

Never performs decoding.

---

detector.py

Owns

Confidence filtering

Label lookup

NMS

Detection objects

---

vision_pipeline.py

Coordinates the entire perception flow.

Applications should primarily call

VisionPipeline.process()

---

display.py

Visualization only.

Supports every learning layer.

Must never modify AI decisions.

---

keyboard.py

Maps user input to current learning layer.

---

decision_engine.py

Consumes detections.

Produces decisions.

No GPIO allowed.

---

action_engine.py

Consumes decisions.

Controls hardware.

GPIO

Speaker

Servo

Relay

LED

---

# 6. Dependency Rules

```
apps
  │
  ▼
vision_pipeline
  │
  ├── camera
  ├── preprocessing
  ├── ai_engine
  ├── detector
  │
  ▼
decision_engine
  │
  ▼
action_engine
```

Rules

Higher layers may depend on lower layers.

Lower layers never depend on higher layers.

Modules communicate only through public APIs.

---

# 7. Naming Conventions

Files

snake_case.py

Classes

PascalCase

Functions

snake_case()

Constants

UPPER_CASE

Private members

_prefix

---

# 8. Adding New Features

Example: Bird Detection

Do NOT modify existing architecture.

Instead

1. Add model.
2. Add labels.
3. Extend detector if needed.
4. Create application.

Architecture remains stable.

---

# 9. Raspberry Pi First

The repository is developed on macOS.

The repository is engineered for Raspberry Pi.

Any feature that cannot execute on Raspberry Pi is incomplete.

---

# 10. Definition of Done

A new module is complete when

✓ Module exists

✓ Public API documented

✓ Unit test written

✓ Executes on Raspberry Pi

✓ Documentation updated

✓ Git committed

---

# 11. Lessons Learned

A predictable repository reduces cognitive load.

Students should spend their time learning AI rather than searching for
where code belongs.

Consistency is a feature, not an afterthought.
