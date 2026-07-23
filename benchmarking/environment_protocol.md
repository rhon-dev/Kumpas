# Benchmarking Environment Conditions Protocol

This document defines the three environmental conditions under which
on-device benchmarks (latency, FPS) are run. Consistent reproduction
is critical for thesis validity.

## Condition Definitions

### 1. Optimal (`optimal`)

| Parameter | Requirement |
|-----------|-------------|
| Lighting | Well-lit room, >300 lux at signer's hands |
| Background | Plain, single-color wall (white/gray/cream) |
| Signer position | Centered in frame, arms-length from camera |
| Measurement | Lux meter reading or phone lux-sensor app screenshot |

**How to reproduce:** Standard indoor overhead fluorescent/LED lighting,
signer facing the light source, plain wall behind. Verify ≥300 lux with
a meter at hand level.

### 2. Low Light (`low_light`)

| Parameter | Requirement |
|-----------|-------------|
| Lighting | Dim, <100 lux at signer's hands |
| Background | Same as optimal (plain wall) |
| Signer position | Same framing as optimal |
| Measurement | Lux meter confirming <100 lux |

**How to reproduce:** Single desk lamp angled away from signer (indirect
bounce light), or evening natural light with no overhead. Turn off
overhead fixtures. Background stays plain so that only illumination
changes as a variable.

### 3. Cluttered Background (`cluttered`)

| Parameter | Requirement |
|-----------|-------------|
| Lighting | Same as optimal (>300 lux) |
| Background | Complex visual scene: bookshelf, other people, varied objects |
| Signer position | Same framing as optimal |
| Measurement | Photo of the setup for reproducibility |

**How to reproduce:** Signer stands in front of a bookshelf or in a room
with multiple objects and/or other people visible. Lighting remains
optimal so that only background complexity changes as a variable.

## Pre-Run Checklist

Before each benchmark run, the tester fills this checklist and records
the condition label in the benchmark log entry:

- [ ] Condition label selected: `optimal` / `low_light` / `cluttered`
- [ ] Lux reading at signer's hand level: ______ lux
- [ ] Background description: _______________
- [ ] Device positioned on tripod / stable surface: yes / no
- [ ] Camera distance to signer: ~_____ cm (target: 60–90 cm)
- [ ] Setup photo taken and saved to `benchmarking/setup_photos/`
- [ ] Duration planned: ≥60 seconds continuous

## Labeling Convention

Use the exact string for the `condition` field in `benchmark_history.json`:
- `"optimal"` — well-lit, plain background
- `"low_light"` — dim (<100 lux), plain background
- `"cluttered"` — well-lit, complex background
- `"n/a"` — offline benchmarks (accuracy) where condition is irrelevant

## Notes

- Only one variable should change per condition (light OR background, not both).
- "Low light + cluttered" is NOT a defined condition — if needed for the thesis,
  add a new condition string and document it here before running.
- Record ambient temperature if device thermal throttling is a concern.
