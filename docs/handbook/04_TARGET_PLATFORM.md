# GuardianAI Engineering Handbook

# Chapter 4 — Target Platform

**Version:** 1.0 (Draft)

---

# 1. Purpose

This document defines the **official execution environment** for GuardianAI_v2.

GuardianAI is developed on a Mac but engineered for the Raspberry Pi.

Whenever there is a conflict between desktop convenience and Raspberry Pi
compatibility, the Raspberry Pi wins.

This document ensures every contributor, including AI coding assistants,
targets the same platform.

---

# 2. Development Philosophy

Development Workstation
- macOS
- VS Code
- Git
- Codex
- Documentation
- Model export (ONNX)

Target Device
- Raspberry Pi
- Camera
- GPIO
- ONNX Runtime
- Real hardware validation

Every feature must eventually execute on the Raspberry Pi.

---

# 3. Hardware Specification

Primary Computer
- Raspberry Pi 4 (4 GB minimum, 8 GB preferred)

Operating System
- Raspberry Pi OS (Bookworm/Trixie compatible)

Camera
- Raspberry Pi Camera Module
- Picamera2 / libcamera

Storage
- 32 GB+ microSD recommended

Power
- Official Pi power supply

Optional Hardware
- OLED Display
- LED
- Buzzer
- Servo
- Relay
- Ultrasonic sensor
- PIR motion sensor
- Environmental sensors

---

# 4. Python Environment

Python Version
- 3.11

Virtual Environment

~/venvs/ai

Project Location

~/Projects/GuardianAI/GuardianAI_v2

Never install project packages globally.

---

# 5. Required Libraries

Core
- numpy
- opencv-python
- onnxruntime
- pillow

Camera
- picamera2

Hardware
- gpiozero

Future
- mediapipe (optional)
- ultralytics (Mac only for training/export)

---

# 6. AI Model Strategy

Training Machine
- macOS workstation

Export Format
- ONNX

Deployment
Copy *.onnx into

models/

Execution
ONNX Runtime only.

No PyTorch dependency on Raspberry Pi.

---

# 7. Performance Goals

Object Detection
Target: 1–3 FPS

Startup
< 30 seconds

Memory
< 1 GB preferred

CPU
ARM CPU only

Offline
100% offline execution supported

---

# 8. Engineering Constraints

Never require:

- CUDA
- TensorRT
- NVIDIA GPU
- Cloud inference
- Internet connectivity

Avoid:
- Excessive memory allocation
- Unnecessary image copies
- Blocking UI loops

Optimize only after correctness.

---

# 9. Repository Assumptions

docs/
Engineering handbook

src/
Reusable modules

apps/
Applications

models/
ONNX models

tests/
Module tests

---

# 10. Camera Pipeline

Reality
↓

Picamera2

↓

NumPy Frame

↓

Preprocessor

↓

Tensor

↓

ONNX Runtime

↓

Detector

↓

Decision Engine

↓

Action Engine

---

# 11. Coding Rules for Raspberry Pi

1. Prefer clarity over micro-optimization.
2. Avoid desktop-only APIs.
3. Keep hardware abstraction separate.
4. Never mix GPIO with AI inference.
5. Every module should run independently.
6. Measure inference time.
7. Handle camera failures gracefully.
8. Provide useful console diagnostics.

---

# 12. Codex Requirements

Before writing code, assume:

Target Platform:
Raspberry Pi

Python:
3.11

Camera:
Picamera2

AI Runtime:
ONNX Runtime

Computer Vision:
OpenCV

GPIO:
gpiozero

No GPU acceleration.

If a proposed solution requires unsupported hardware or software,
propose a Raspberry Pi compatible alternative.

---

# 13. Deployment Workflow

Mac
↓
Implement
↓
Commit
↓
Copy to Raspberry Pi
↓
Install dependencies
↓
Run
↓
Observe
↓
Refine

The Raspberry Pi is the source of truth.

---

# 14. Definition of Done

A feature is complete only when:

✓ Code runs on Raspberry Pi
✓ Camera tested
✓ AI inference verified
✓ Hardware interactions verified
✓ Documentation updated
✓ No platform-specific assumptions remain

---

# 15. Lessons Learned

Embedded AI development differs from desktop AI.

The Raspberry Pi's limitations are intentional educational constraints.
Designing within them encourages efficient software, modular architecture,
and a deeper understanding of how intelligent systems operate on real
hardware rather than idealized development machines.
