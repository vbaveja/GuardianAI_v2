# GuardianAI Engineering Handbook

# Chapter 5 — Design Philosophy

**Version:** 1.0 (Draft)

---

# Purpose

This document defines the principles that guide every architectural and
implementation decision in GuardianAI.

Unlike the Architecture document, which may evolve as technology changes,
the Design Philosophy should remain relatively stable. It answers the
question:

**"What kind of engineering team do we want to be?"**

This document should be read by every contributor and by every AI coding
assistant before writing code.

---

# The North Star

GuardianAI is not an object detection project.

GuardianAI is an educational platform that uses computer vision to teach
students how intelligent systems perceive, understand, reason, and act.

Every design decision should reinforce learning.

---

# Core Philosophy

## 1. Education Before Optimization

Readable code is preferred over clever code.

If a design is slightly slower but significantly easier for students to
understand, prefer the simpler design.

---

## 2. Raspberry Pi First

GuardianAI is engineered for affordable, real hardware.

The Raspberry Pi is the target platform.

Desktop development exists only to accelerate iteration.

---

## 3. One New Idea Per Layer

Every learning layer introduces exactly one major concept.

Students should never have to learn multiple difficult ideas
simultaneously.

---

## 4. AI Must Never Feel Like Magic

Every stage should be observable.

Students should be able to answer:

- What went into the model?
- What came out?
- Why was this object detected?
- What happened next?

---

## 5. Separate Perception, Reasoning and Action

These are independent concerns.

Perception answers:

"What do I see?"

Reasoning answers:

"What should I do?"

Action answers:

"How do I interact with the world?"

Keeping these separate makes the platform easier to understand, test and
extend.

---

## 6. Build Reusable Modules

Every reusable capability belongs in src/.

Applications should assemble modules rather than duplicating logic.

---

## 7. Favor Stable Interfaces

Public APIs should change slowly.

Internal implementations may evolve.

Stable interfaces reduce maintenance and simplify teaching.

---

## 8. Make Every Stage Visible

Visualization is not debugging.

Visualization is part of learning.

Whenever practical, display:

- Original frame
- Grayscale
- Blur
- Edges
- Motion
- AI input
- Detections
- Decisions

---

## 9. Simplicity Scales

The first implementation should be the simplest correct implementation.

Complexity should be introduced only when it provides clear educational or
engineering value.

---

## 10. Build for Extension

Today's object detector should become tomorrow's:

- Garden Guardian
- Parking Assistant
- Wildlife Monitor
- Rover Vision
- Face Recognition

The architecture should welcome new applications without major redesign.

---

# Engineering Principles

- One responsibility per module.
- One public purpose per file.
- Small, testable components.
- Documentation evolves with code.
- Manual Raspberry Pi validation is mandatory.
- Optimize only after correctness.

---

# Codex Design Rules

Before implementing a feature, Codex should ask:

1. Does this follow the architecture?
2. Does this improve learning?
3. Does it keep modules independent?
4. Will it execute on Raspberry Pi?
5. Can a student understand it?

If the answer to any question is "no", reconsider the implementation.

---

# Decision Framework

When choosing between two designs:

1. Correctness
2. Educational clarity
3. Maintainability
4. Raspberry Pi compatibility
5. Performance

Performance is intentionally last unless requirements demand otherwise.

---

# Anti-Patterns

Avoid:

- Monolithic files
- Hidden global state
- Tight coupling
- Hardware mixed with AI logic
- Duplicate code
- Desktop-only assumptions
- Magic numbers without explanation

---

# Definition of Success

GuardianAI succeeds when:

- Students understand the pipeline.
- New applications reuse existing modules.
- Contributors quickly understand the repository.
- Codex generates consistent code.
- The platform remains approachable after years of growth.

---

# Lessons Learned

Technology will change.

Models will improve.

Hardware will evolve.

The philosophy should remain stable.

GuardianAI exists to create builders, not just users.

Every line of code should move a student one step closer to understanding
how intelligent machines work.
