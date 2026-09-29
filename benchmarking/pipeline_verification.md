# Shipped-pipeline verification: offline status (2026-09-29)

**Status: incomplete.** These checks do not establish Android/Python detector parity, anatomical handedness, real-phone recognition, or camera-to-feedback latency.

## Executed locally

- Prepared `../kumpas-data/clips_raw/clips/22/10.MOV` as 30 uniformly selected lossless PNG frames under `../kumpas-data/parity/clips_22_10_30/`. The source decoder saw 244 frames; selected original indices run from 0 to 243. Each PNG is SHA-256 recorded in `manifest.json`. Uniform subsampling changes MediaPipe tracking history versus full-video extraction.
- Ran Python Holistic over those 30 PNGs; the normalized, 258-dimensional reference is `../kumpas-data/parity/clips_22_10_30_python.json`. It is *not* an Android output.
- Compiled and executed `FeatureNormalizer.kt` on the local JVM. A synthetic pose/right-hand vector agrees numerically with `build_sequences.normalize` in the cross-language unit test. This tests normalization for that case only, not detector equality. `VisionEngine` now calls the same extracted Kotlin normalizer without changing its algorithm.
- Found a **known feature-parity gap:** when a hand is detected but pose is absent, Python training normalization sets the whole frame to zero, whereas the existing Android normalization leaves that hand block nonzero. This extraction preserves existing shipped behavior; do not interpret parity as established or silently change the live path without controlled evaluation.
- The dataset clips have no independently verified anatomical left/right annotation here. `handedness()` label agreement between detectors cannot prove anatomical correctness.

## Reproduce offline checks

From repo root with the local Python environment and cached Kotlin compiler:

```bash
training/.venv/bin/python -m unittest benchmarking/test_pipeline_parity.py benchmarking/test_python_reference.py benchmarking/test_kotlin_normalization_parity.py -v
training/.venv/bin/python -m unittest discover -s training/tests -p 'test_*.py' -v
python benchmarking/compile_feature_smoke.py
```

To generate a new reference, choose **new** output paths under ignored `../kumpas-data/parity/` (these commands refuse to overwrite existing output):

```bash
training/.venv/bin/python benchmarking/pipeline_parity.py prepare ../kumpas-data/clips_raw/clips/22/10.MOV ../kumpas-data/parity/new_clip --max-frames 30
training/.venv/bin/python benchmarking/pipeline_parity.py reference ../kumpas-data/parity/new_clip ../kumpas-data/parity/new_clip_python.json
```

The host comparator accepts an **actual Android feature JSON** with the same frame indices, PNG SHA-256s, 258 features per frame and boolean `pose_seen`, `left_seen`, `right_seen` flags:

```bash
training/.venv/bin/python benchmarking/pipeline_parity.py compare ../kumpas-data/parity/new_clip_python.json ../kumpas-data/parity/new_clip_android.json ../kumpas-data/parity/new_clip_report.json
```

No Android feature JSON has been generated. Do not use a duplicate Python reference as a purported Android run.

## Remaining gates

1. **Android toolchain:** `./gradlew :app:testDebugUnitTest --tests com.kumpas.kumpas_app.FeatureNormalizerTest --offline` fails at Flutter plugin resolution: `app/android/local.properties` points to `/Users/Develop/flutter`, which does not exist on this machine. The installed Flutter executable resolves under `/opt/homebrew/share/flutter`; the configured Android SDK directory is also absent. The standalone Kotlin smoke is **not** an Android app build.
2. **Identical-frame replay:** implement and compile an Android harness that reads the prepared PNGs in order, verifies each hash, runs the exact live MediaPipe extractor, and exports vectors/flags. Compare observed JSON to the Python reference with the existing comparator. Detector implementations differ, so report error/disagreement rather than assuming numerical identity.
3. **Anatomical handedness:** require consenting, independently labeled left-only/right-only calibration on the actual front-camera path or independently verified frame labels. Until then label `unverified`.
4. **Physical target-class phone:** record camera-analyzer callback, bitmap conversion, detector, model inference, feedback generation, main-thread event delivery and, separately, UI presentation. Report collection interval and last sampled frame-to-feedback latency as distinct measures; include device identity, build/model hashes, conditions, sample count, p50/p95, dropped-frame behavior, and per-class recognition. None are measured here.

Keep replay media and frame-level feature vectors out of Git.
