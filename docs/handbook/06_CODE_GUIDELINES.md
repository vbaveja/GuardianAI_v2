# GuardianAI Engineering Handbook

# Chapter 6 — Code Guidelines

**Version:** 1.0 (Draft)

---

# 1. Purpose

This document defines how GuardianAI code should be written.

Its goal is consistency, readability, maintainability, and Raspberry Pi compatibility.

Every human contributor and every AI coding assistant should follow these guidelines.

---

# 2. Primary Principles

1. Readability before cleverness.
2. Raspberry Pi first.
3. One responsibility per module.
4. Small, testable functions.
5. Stable public APIs.
6. Explain intent, not obvious syntax.
7. Documentation evolves with code.

---

# 3. Python Version

Target: Python 3.11

Avoid features that are unavailable on Raspberry Pi OS.

---

# 4. File Organization

Each source file should contain:

- Module docstring
- Imports
- Constants
- Classes
- Public methods
- Private helpers
- Main block (only for testing)

One primary class per file whenever practical.

---

# 5. Module Template

```python
"""Module description."""

from pathlib import Path

class Example:
    """Single responsibility."""

    def public_method(self):
        pass

    def _private_helper(self):
        pass
```

---

# 6. Naming Conventions

Files:
snake_case.py

Classes:
PascalCase

Functions:
snake_case()

Variables:
snake_case

Constants:
UPPER_CASE

Private members:
_prefix

Avoid abbreviations unless universally understood.

---

# 7. Imports

Preferred order:

1. Standard library
2. Third-party packages
3. GuardianAI modules

Avoid wildcard imports.

---

# 8. Docstrings

Every public class and public function requires a docstring.

Document:

Purpose

Arguments

Returns

Exceptions (if applicable)

---

# 9. Type Hints

Prefer explicit type hints for public APIs.

Example:

```python
def infer(tensor: np.ndarray) -> np.ndarray:
    ...
```

---

# 10. Logging

Use clear console messages.

Good:

Loading ONNX model...

Inference completed in 215 ms

Bad:

Done.

Avoid excessive console output during normal operation.

---

# 11. Error Handling

Never silently ignore exceptions.

Provide meaningful diagnostics.

Gracefully handle:

- Camera unavailable
- Model missing
- Label file missing
- GPIO unavailable

---

# 12. Performance

Correctness first.

Then measure.

Avoid:

- Unnecessary image copies
- Large temporary allocations
- Blocking UI loops

Measure inference time where appropriate.

---

# 13. Raspberry Pi Rules

Do not assume:

- CUDA
- GPU
- Internet
- Desktop-only libraries

Target CPU execution using ONNX Runtime.

---

# 14. Testing

Every reusable module should have a corresponding test.

Examples:

camera.py
→ test_camera.py

detector.py
→ test_detector.py

Tests should be small, deterministic, and easy to understand.

---

# 15. Code Review Checklist

Before merging, verify:

✓ Follows architecture

✓ Single responsibility

✓ Public APIs documented

✓ Raspberry Pi compatible

✓ Unit test added

✓ Documentation updated

---

# 16. Codex Implementation Rules

Before writing code:

Read:

01_VISION.md

05_DESIGN_PHILOSOPHY.md

04_TARGET_PLATFORM.md

02_ARCHITECTURE.md

03_PROJECT_SKELETON.md

06_CODE_GUIDELINES.md

When implementing:

- Stay within requested scope.
- Do not reorganize architecture.
- Do not introduce new dependencies without approval.
- Prefer extending existing modules.
- If architecture changes are required, stop and explain why.

---

# 17. Good vs Bad Examples

Good

- Clear function names
- Short methods
- Independent modules
- Explicit dependencies

Bad

- 500-line files
- Hidden global state
- Mixed AI and GPIO logic
- Duplicate code
- Hard-coded paths
- Magic numbers without explanation

---

# 18. Definition of Done

A feature is complete only when:

✓ Code is readable

✓ Raspberry Pi tested

✓ Unit tests pass

✓ Documentation updated

✓ Git committed

---

# Lessons Learned

GuardianAI code should be understandable by a student six months after writing it.

Readable software is an educational asset.

Consistency across the repository is more valuable than individual programming style.
