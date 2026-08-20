# GuardianAI Engineering Handbook

# Chapter 2 — Architecture

**Version:** 1.0 (Draft)

---

# 1. Purpose

This document defines the software architecture of GuardianAI_v2.

It explains:

- Why the architecture exists
- The major software components
- How data flows through the system
- Public interfaces
- Design rules
- Future expansion

This document is the primary engineering reference for all development.

---

# 2. Architectural Goals

GuardianAI has four primary goals.

1. Teach AI, not hide AI.
2. Keep modules independent.
3. Make every processing stage observable.
4. Build reusable software for future PiPal-AI projects.

---

# 3. High-Level Architecture

Reality
↓
Camera
↓
Vision Pipeline
↓
Decision Engine
↓
Action Engine
↓
Physical World

The Vision Pipeline transforms raw pixels into semantic understanding.

---

# 4. Vision Pipeline

Camera Capture
↓
Preprocessing
↓
AI Inference
↓
Prediction Decoding
↓
Object Recognition
↓
Reasoning
↓
Action

Every GuardianAI application follows this pipeline.

Applications should never bypass pipeline stages.

---

# 5. Layers of Perception

Layer 0 – Reality
Purpose:
Display the untouched camera frame.

Input:
Camera frame.

Output:
Original image.

Student learns:
What the camera actually captures.

---

Layer 1 – Brightness

Purpose:
Convert color into grayscale.

Student learns:
Color is optional for many vision tasks.

---

Layer 2 – Simplification

Purpose:
Reduce noise through blurring.

Student learns:
Removing detail can improve robustness.

---

Layer 3 – Boundaries

Purpose:
Highlight edges.

Student learns:
Objects are often identified through boundaries.

---

Layer 4 – Change

Purpose:
Detect motion by comparing frames.

Student learns:
Vision can understand change without AI.

---

Layer 5 – AI Vision

Purpose:
Show the exact 640x640 letterboxed image entering the neural network.

Student learns:
The AI never sees the original camera image.

---

Layer 6 – AI Hypotheses

Purpose:
Expose raw neural network predictions.

Student learns:
The network proposes thousands of hypotheses before filtering.

---

Layer 7 – Understanding

Purpose:
Convert predictions into recognized objects.

Student learns:
Recognition requires confidence filtering and decoding.

---

Layer 8 – Localization

Purpose:
Associate recognized objects with locations.

Student learns:
Detection answers both WHAT and WHERE.

---

Layer 9 – Reasoning

Purpose:
Transform observations into decisions.

Example:
If squirrel detected -> play deterrent sound.

Student learns:
AI recognition is different from decision making.

---

Layer 10 – Action

Purpose:
Interact with the physical world.

Examples:
LED
Speaker
Servo
Notification

Student learns:
Intelligence becomes meaningful only when connected to action.

---

# 6. Software Components

camera.py
Captures frames.

preprocessing.py
Prepares tensors.

ai_engine.py
Executes ONNX Runtime.

detector.py
Converts raw predictions into Detection objects.

vision_pipeline.py
Coordinates the complete perception pipeline.

display.py
Visualizes learning layers.

keyboard.py
Controls current layer.

decision_engine.py
Produces decisions.

action_engine.py
Executes hardware actions.

---

# 7. Dependency Rules

Applications

↓

VisionPipeline

↓

Camera
Preprocessor
AIEngine
Detector

↓

DecisionEngine

↓

ActionEngine

Rules:

- Lower layers never import higher layers.
- Hardware control never occurs inside AI modules.
- Applications communicate through VisionPipeline whenever possible.

---

# 8. Public Interfaces

Camera
- start()
- capture()
- stop()

Preprocessor
- process(frame)

AIEngine
- load(model)
- infer(tensor)

Detector
- detect(raw_output)

VisionPipeline
- process(frame)
- set_layer(layer)

DecisionEngine
- evaluate(objects)

ActionEngine
- execute(decision)

---

# 9. Extension Model

Future modules should plug into the architecture without modifying the
existing pipeline.

Examples:

Garden Guardian
Parking Assistant
Bird Identifier
Face Recognition

Only DecisionEngine and ActionEngine should require application-specific logic.

---

# 10. Design Rules

- One responsibility per module.
- Public APIs remain stable.
- Explain every processing stage.
- Raspberry Pi is the target platform.
- Optimize only after correctness.
- Visualization is part of learning.

---

# 11. Lessons Learned

The architecture intentionally separates:

Perception

↓

Understanding

↓

Reasoning

↓

Action

This mirrors modern robotics and AI systems while also providing a natural
educational progression.

The architecture should remain stable even if individual AI models,
libraries, or hardware evolve.
