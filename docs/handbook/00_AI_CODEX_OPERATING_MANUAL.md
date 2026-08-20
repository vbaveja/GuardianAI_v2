# GuardianAI Engineering Handbook

# 00_Codex_Operating_Manual

Version: 1.0 (Draft)

## Purpose

This document is written specifically for AI coding assistants (Codex) that
contribute to GuardianAI.

It defines how code should be developed, what assumptions are valid, when to
stop and ask questions, and how to work within the GuardianAI architecture.

This document complements—not replaces—the Architecture, Design Philosophy,
Target Platform, Project Skeleton, and Code Guidelines.

---

# Mission

Your role is to implement software that faithfully follows the GuardianAI
architecture.

Your goal is NOT to redesign the project.

Your goal is to produce clean, maintainable, Raspberry Pi compatible code that
helps students learn how AI systems work.

---

# Read These Documents First

Always read the following in order before implementing code.

1. 01_VISION.md
2. 05_DESIGN_PHILOSOPHY.md
3. 04_TARGET_PLATFORM.md
4. 02_ARCHITECTURE.md
5. 03_PROJECT_SKELETON.md
6. 06_CODE_GUIDELINES.md

Do not begin implementation until you understand these documents.

---

# Standard Session Workflow

Step 1
Read the handbook.

Step 2
Summarize your understanding.

Step 3
State assumptions.

Step 4
Identify architecture impacts.

Step 5
Wait if clarification is required.

Step 6
Implement only the requested feature.

Step 7
Explain what changed.

Step 8
Recommend tests.

---

# Raspberry Pi First

Assume every feature must execute on:

- Raspberry Pi 4
- Python 3.11
- ONNX Runtime
- Picamera2
- OpenCV
- gpiozero

Never introduce dependencies that require:
- CUDA
- TensorRT
- NVIDIA GPUs
- Internet connectivity
- Cloud inference

If a proposal violates these assumptions, stop and suggest a Pi-compatible
alternative.

---

# Scope Control

Implement only the requested task.

Do NOT:
- reorganize the repository
- rename unrelated files
- refactor unrelated modules
- introduce new frameworks
- replace working code without approval

When architecture changes appear necessary, explain why and wait.

---

# Preferred Development Style

Implement in small increments.

Each pull request or commit should ideally contain:
- one feature
- one bug fix
- one refactoring
- one documentation update

Avoid combining unrelated work.

---

# Module Ownership

camera.py
Capture images.

preprocessing.py
Prepare tensors.

ai_engine.py
Run inference.

detector.py
Decode predictions.

vision_pipeline.py
Coordinate perception.

decision_engine.py
Convert observations into decisions.

action_engine.py
Execute hardware actions.

Never mix responsibilities.

---

# Coding Expectations

Every public function should:
- have a docstring
- use clear names
- be independently testable

Prefer:
- composition
- small methods
- explicit dependencies

Avoid:
- hidden globals
- duplicate code
- magic numbers
- monolithic classes

---

# Output Format

When completing a task, provide:

1. Summary
2. Files modified
3. New public APIs
4. Testing instructions
5. Future improvements (optional)

---

# Testing Expectations

Recommend:
- unit tests
- Raspberry Pi validation
- camera validation
- performance measurements when appropriate

Do not claim hardware support unless the code is designed for it.

---

# When to Stop

Stop and ask for guidance if:
- architecture conflicts arise
- requirements are ambiguous
- a new dependency is required
- public APIs must change
- repository organization must change

---

# Definition of Success

A successful implementation:
- follows the handbook
- keeps the architecture clean
- is understandable by students
- runs on Raspberry Pi
- is easy to extend
- improves the learning experience

---

# Guiding Principle

GuardianAI is an educational platform first.

Every implementation should make the software easier to understand,
not merely more sophisticated.

If two solutions are technically equivalent, choose the one that best
supports learning and long-term maintainability.
