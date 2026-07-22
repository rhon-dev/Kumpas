# Phase 2 — Related Work Grounding

## 1. Positioning Summary

Kumpas sits at the intersection of three research threads: (a) Filipino Sign Language recognition, (b) on-device/real-time sign classification, and (c) corrective feedback for sign language learners. Existing work in thread (a) and (b) is mature enough that classification itself is not novel. Thread (c) — particularly for FSL and particularly on-device — is where Kumpas contributes.

---

## 2. Related Work by Category

### 2.1 Filipino Sign Language Recognition Systems

| System | Year | Approach | Scope | Gap Kumpas Fills |
|--------|------|----------|-------|-----------------|
| **FSL-105 dataset** (Tupal & Villaverde, Mendeley 2023; [SSRN paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4476867)) | 2023 | First large-scale FSL video dataset: 105 signs, 2130 clips | Dataset contribution only — no app, no feedback | Kumpas builds on this dataset but adds the feedback layer |
| **FSL CNN-LSTM** (Springer, 2024; [link](https://link.springer.com/chapter/10.1007/978-3-031-47724-9_8)) | 2024 | CNN-LSTM on 15 FSL phrases, 450 videos, 98% accuracy | Lab-accuracy recognition; no on-device deployment, no feedback | High accuracy but limited vocabulary, no learner-facing system |
| **FSL LSTM+ResNet** (ResearchGate, 2023; [link](https://www.researchgate.net/publication/362747600)) | 2023 | LSTM (94%) vs ResNet (87%) on 15 continuous FSL phrases | Classification only, offline analysis | No real-time capability, no feedback |
| **Transactional FSL with GRU** (MDPI, 2025; [link](https://www.mdpi.com/2673-4591/134/1/47)) | 2025 | MediaPipe + GRU, 26 transactional signs, Raspberry Pi 5 | Edge deployment (Pi 5), but translation/recognition only | Runs on edge hardware but provides no corrective guidance |
| **FSL CNN-LSTM real-time** (MDPI, 2024; [link](https://www.mdpi.com/2673-9585/4/3/20)) | 2024 | CNN-LSTM, 15 expressions, 98% accuracy, real-time | Dynamic gesture recognition with real-time processing | Recognition only — does not tell the learner what to fix |
| **SENYAS** ([senyas.vercel.app](https://senyas.vercel.app/)) | 2024 | Camera feed → model prediction → text output | Web-based FSL translator | Translation tool, not instructional; no feedback loop |
| **Letras sa Senyas** ([site](http://letras-sa-senyas.vercel.app/)) | — | Mobile FSL learning with video demos + real-time alphabet recognition | Learning app with recognition | Offers instructional content but no per-dimension corrective feedback |
| **Sign-Bridge** ([paper](https://innocon.innotcs.org/index.php/best/article/download/204/271)) | — | Two-way FSL translation (text→gesture, gesture→text) via deep learning | Communication tool | Translation, not instruction; no feedback on learner's form |

**Summary:** FSL recognition systems consistently achieve high classification accuracy (94–98%) using CNN-LSTM or GRU architectures with MediaPipe landmarks. However, none provide corrective feedback to help a learner improve their signing. They answer "what sign is this?" but never "what did you do wrong?"

### 2.2 Corrective Feedback Systems for Sign Language Learners

| System | Year | Sign Language | Feedback Type | Platform | Gap vs. Kumpas |
|--------|------|--------------|---------------|----------|----------------|
| **SignTutor** (Aran et al., IEEE 2009; [link](https://www.researchgate.net/publication/224394273)) | 2009 | Turkish SL | Multimodal feedback on hand shape features; evaluates signing correctness | Desktop + external sensors | Pioneering work but requires specialized hardware (not phone camera); limited to hand shape features; not FSL |
| **Learn2Sign** (ASU, 2021; [link](https://www.researchgate.net/publication/349623234)) | 2021 | ASL | Fine-grained feedback on location, movement, and hand-shape via explainable AI; modular "waterfall" architecture | Desktop/web | Closest analog to Kumpas — provides per-dimension feedback. But: ASL only, not on-device/mobile, requires server-side processing, not real-time |
| **Chinese SL MR Teaching** (arXiv 2404.10490, 2024) | 2024 | Chinese SL | Multi-dimensional feedback via Mixed Reality; ternary evaluation algorithm for comprehensive assessment | VR/AR headset (HoloLens-class) | Requires MR hardware; not accessible on a phone; Chinese SL; very different deployment context |
| **SA-SL Tutor** (Oliveira, 2014; [link](https://www.researchgate.net/publication/269274643)) | 2014 | South African SL | Context-sensitive detailed feedback | Desktop + Kinect | Kinect-dependent; not mobile; SASL only |
| **HNS-based wearable system** (ACM IMWUT, 2020; [link](https://dl.acm.org/doi/10.1145/3432211)) | 2020 | German SL (DGS) | Real-time feedback matched to Hamburg Notation System features | Wearable sensors (IMU-based) | Requires sensor hardware; not vision-based; not phone-accessible |
| **ASL Practice** ([practice.deafened.org](https://practice.deafened.org/)) | 2025 | ASL | Instant feedback on handshape, movement, location using ASL-LEX data | Web browser | Web-only, ASL-only, requires internet, not FSL |

**Summary:** Corrective-feedback systems exist but are characterized by: (a) requiring specialized hardware (Kinect, wearable sensors, MR headsets), (b) being limited to ASL/DGS/Turkish SL (never FSL), (c) requiring server-side processing or internet connectivity, or (d) providing only binary/overall feedback rather than per-dimension guidance. No existing system provides per-dimension corrective feedback for FSL on a standard smartphone, fully offline.

### 2.3 On-Device/Real-Time Sign Classification (Architecture Context)

| Work | Year | Architecture | Performance | Relevance |
|------|------|-------------|-------------|-----------|
| **Dynamic Kannada SL on mobile** (Nature Scientific Reports, 2026; [link](https://www.nature.com/articles/s41598-026-40181-7)) | 2026 | BiLSTM + PTQ → TFLite; 95.71% accuracy, 27.8ms inference | Demonstrates TFLite quantized LSTM models achieve high accuracy with low latency on mobile | Validates Kumpas's architectural choice (LSTM + TFLite quantization) |
| **TinyMSLR** (Nature, 2026; [link](https://www.nature.com/articles/s41598-026-38478-8)) | 2026 | Hybrid CNN-Transformer, <2.7M params, 24ms CPU inference | Edge-optimized with knowledge distillation | Shows CNN+attention models fit on-device; validates Kumpas's parameter-budget approach |
| **Real-time SL translation** (arXiv 2510.13137, 2025) | 2025 | 3D CNN (92.4%) vs LSTM (86.7%); CNN requires 3.2% more processing | Tradeoff analysis between accuracy and latency | Supports Kumpas's CNN-LSTM hybrid as balanced approach |

---

## 3. Novelty Statement

> **Kumpas is the first system to provide real-time, per-dimension corrective feedback (handshape, orientation, motion, timing) for Filipino Sign Language learners, running entirely on-device on a standard mid-range Android smartphone without internet connectivity.**

Specifically, Kumpas's contributions relative to existing work are:

1. **FSL-specific feedback (vs. Learn2Sign, SignTutor, ASL Practice):** Existing feedback systems target ASL, DGS, Turkish SL, or Chinese SL. No corrective-feedback system exists for FSL.

2. **On-device, offline (vs. Learn2Sign, ASL Practice, Chinese SL MR):** Existing feedback systems require server-side processing, internet connectivity, or specialized hardware (Kinect, wearable sensors, MR headsets). Kumpas runs entirely on a standard phone camera with no network dependency.

3. **Four-dimension feedback (vs. SignTutor, binary systems):** While SignTutor addressed hand shape features and Learn2Sign covered location/movement/hand-shape, Kumpas provides structured feedback across handshape, orientation, motion path, AND timing — with the timing dimension being particularly under-addressed in prior work.

4. **Accessible hardware (vs. wearable/sensor systems):** The HNS-based wearable system and data-glove approaches require specialized sensors. Kumpas uses only the phone's built-in camera, making it accessible to any learner with a mid-range Android device.

What Kumpas does NOT claim:
- Novel CNN-LSTM architecture for sign classification (established technique)
- Novel use of MediaPipe for landmark extraction (existing tool)
- Novel TFLite quantization methodology (standard technique)
- State-of-the-art classification accuracy (95% is competitive but not the point)

The classification pipeline is a necessary prerequisite; the corrective-feedback layer is the contribution.

---

## 4. Gap Analysis Table

| Capability | FSL Systems | Non-FSL Feedback Systems | Kumpas |
|------------|------------|--------------------------|--------|
| FSL support | ✅ | ❌ | ✅ |
| Real-time classification | ✅ (some) | ✅ (some) | ✅ |
| Per-dimension feedback | ❌ | ✅ (partial) | ✅ (4 dimensions) |
| On-device / offline | ❌ (mostly web/lab) | ❌ (mostly server/hardware) | ✅ |
| Standard phone camera | ✅ (some) | ❌ (Kinect/sensors/MR) | ✅ |
| Timing feedback | ❌ | ❌ (rarely) | ✅ |
| Learner-facing app | ❌ (research demos) | ✅ (some) | ✅ |

---

## 5. Citation List (for thesis literature review)

### FSL Recognition
1. Tupal, I.J.L. & Villaverde, J. (2023). "The Video Filipino Sign Language Sign Database of Introductory 105 FSL Signs." Mendeley Data / SSRN 4476867.
2. [FSL CNN-LSTM] Springer LNCS (2024). "Gesture Recognition of Filipino Sign Language Using Convolutional and Long-Short Term Memory Neural Network." Chapter in Springer.
3. [FSL LSTM+ResNet] (2023). "Filipino Sign Language Recognition Using Long Short-Term Memory and Residual Network Architecture." ResearchGate.
4. [Transactional FSL GRU] MDPI Engineering Proceedings 134(1):47 (2025). "Development of Transactional Filipino Sign Language Recognition System Using MediaPipe and Gated Recurrent Units."
5. [FSL CNN-LSTM real-time] MDPI (2024). "Gesture Recognition of Filipino Sign Language Using CNN and Long Short-Term Memory Deep Neural Networks."

### Corrective Feedback for Sign Language
6. Aran, O. et al. (2009). "SignTutor: An Interactive System for Sign Language Tutoring." IEEE FG 2009.
7. Tornay, S. et al. (2021). "Learn2Sign: Explainable AI for Sign Language Learning." ASU / ACM IUI.
8. [Chinese SL MR] (2024). "Teaching Chinese Sign Language with Feedback in Mixed Reality." arXiv:2404.10490.
9. Oliveira, T. (2014). "A Vision-based South African Sign Language Tutor." Dissertation.
10. [HNS wearable] (2020). ACM IMWUT. "Real-time feedback matched to Hamburg Notation System features."

### On-Device / Edge Deployment
11. [Kannada SL TFLite] Nature Scientific Reports (2026). "Dynamic Kannada Sign Language Recognition on Resource Constrained Devices."
12. [TinyMSLR] Nature (2026). "An explainable hybrid CNN-Transformer model for sign language recognition on edge devices."
13. [Real-time SL] arXiv:2510.13137 (2025). "Real-Time Sign Language to Text Translation using Deep Learning."

### Context / Communication Systems
14. Sign-Bridge (FSL two-way translation app). InnoTCS Proceedings.
15. SENYAS (FSL web translator). senyas.vercel.app.

---

## 6. Honest Limitations of This Positioning

- The thesis should acknowledge that Learn2Sign (ASU, 2021) provides per-dimension feedback for ASL and is the closest existing analog. Kumpas's differentiation is: FSL-specific, on-device/offline, and adds the timing dimension.
- The 2026 Chinese SL MR paper shows multi-dimensional feedback is an active area. Kumpas differentiates by running on standard hardware (phone) rather than MR headsets.
- ASL Practice (deafened.org, 2025) is a web-based system providing similar per-dimension feedback for ASL. If this system were adapted to FSL and made offline, it would overlap significantly with Kumpas's contribution. The thesis should note this and argue that offline/on-device accessibility is a meaningful differentiator for learners in the Philippines who may have limited connectivity.
- The "timing" dimension in Kumpas's feedback is the least-addressed in prior work and thus the least-validated aspect — the thesis should be transparent that this dimension's feedback quality is more exploratory.

---

## Status

**Complete.** Ready for author review and approval before proceeding to Phase 3 formalization.
