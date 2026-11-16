# Current-state audit — published original repository

## Identity and scope

Audited published main commit `4d901693642af5f572455b2c75ba095b0ec65c7f` in the new local `holistic-migration` branch. The original cloud checkout and separate Recognition V2 worktree remain untouched. Unpublished local changes and ignored model binaries are not established by this audit.

## Verified baseline

| Area | Actual implementation | Evidence |
|---|---|---|
| Dataset source | FSL-105 raw MOV recordings, imported from train/test CSVs and clips.zip; no webcam training collector | `training/preprocessing/dataset_audit.py`, `extract_landmarks.py:92–126,162–195` |
| Extraction | Legacy Python `mp.solutions.holistic.Holistic`; pose 33×4, face468×3, left21×3, right21×3 | `extract_landmarks.py:45–89` |
| Stored frame features | Float32 1,662; zero-filled missing components | `extract_landmarks.py:61–89,145–155` |
| Historical classifier features | 258 without face: all33 pose XY Z/visibility plus both21-point XYZ hands | `build_sequences.py:23–25,118–123`; `VisionEngine.kt:17–27,51–56` |
| Sequence | Default30 rows; uniform whole-clip sampling, repeating last row for short clips | `build_sequences.py:47–51,93–94` |
| Normalization | Hip midpoint origin and torso-distance scale; individually missing hand blocks restored to zero | `build_sequences.py:54–84` |
| Architecture | Temporal Conv1D64/128, BatchNorm, MaxPool2, LSTM128/64, Dense128, Dense50 softmax, dropout0.4 | `training/models/train_cnn_lstm.py:65–86,94–102` |
| Label mapping | All50 approved labels; dense indices follow ascending original IDs. Dense25 is original49 TODAY | `selected_classes.json`; `build_sequences.py:97–101` |
| Application extraction | Separate Tasks PoseLandmarker and HandLandmarker; not a unified Holistic graph | `VisionEngine.kt:9–10,170–208`; `VisionResourceFactory.kt:20–35` |
| Application tensor | Source constructs Float32 `[1,30,258]`, output `[1,50]` | `VisionEngine.kt:51–54,241–244,286–289` |
| Application timing | Every4th analyzer frame; 30 selected observations. Window duration depends on actual throughput | `VisionEngine.kt:149–158,220–244` |

The original project is therefore not a 63-feature hand-only classifier. The approved new work is an isolated shared Holistic training/Mac pipeline and all-gesture retraining, preserving the CNN-LSTM family and exact existing output mapping.

## Material findings

1. **Train/serve mismatch:** training uses unified legacy Holistic, while Android uses independent Pose/Hands. Equal dimensions do not establish equal detector outputs, anatomy or temporal behavior. Phone fixes are outside this migration scope.
2. **Missing-pose disagreement:** Python zeros the whole frame when pose is absent; Kotlin preserves raw hand values. The new contract must choose one fail-closed behavior consistently.
3. **Missing-hand augmentation defect:** `training/augmentation/augment_landmarks.py:52–67` detects absence jointly across both hands. Translation can turn an individually absent hand into nonzero coordinates. An independent audit reproduced this in memory for both supported layouts. Preserve the historical implementation and use individually masked transformations in the new candidate path rather than inheriting it silently.
4. **Notebook divergence:** the notebook still validates on augmented rows and consults test during the training workflow. The independent source/RNG audit reconstructed fit siblings for every validation row; this is lineage reconstruction, not a fresh historical accuracy measurement. Use the original-clip split protocol, not that notebook, for new runs.
5. **Tracker/cache identity:** the legacy extractor reuses a worker tracker across clips and skips existing NPZ outputs by filename existence alone. These are source-derived risks, not demonstrated contamination. New extraction needs a new detector per clip plus source/configuration/contract binding.
6. **Temporal/representation issue:** the existing diagnosis attributes weak classes to whole-clip rest sampling and shoulder/handshape signal differences. Those analyses are historical recorded observations, not newly reproduced detector recall or proof that a smaller contract will fix accuracy.
7. **Export is not drop-in:** frozen export and reference assets assume30×258; existing gold standards are50×30×258. A new candidate must not overwrite that asset tuple. Historical test use and unknown signer IDs remain limitations.
8. **Environment mismatch:** repository preprocessing requirements list legacy MediaPipe; the compatible resident combined environment actually exposes Tasks Holistic1.2.0 without legacy `mp.solutions`. Use verified installed signatures and retain exact dependencies; do not patch the environment to emulate old APIs.

## Fresh verification

- Published clone populated cleanly on local branch `holistic-migration`.
- Existing training tests: **51 passed**, including a synthetic frozen-export/interpreter exercise. Warnings were emitted. No all-gesture model was trained.
- `uv pip check` for the chosen resident environment: **56 packages checked; all compatible**.
- Actual Tasks Holistic VIDEO execution succeeded on two synthetic blank RGB frames at timestamps0 and67ms, with correctly empty component results. This does not prove human tracking or recognition.
- Downloaded official Holistic task bundle:13,683,609 bytes, SHA-256 `e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8`. Exact receipt is external to Git.

## Current real data inventory

Recovered official Mendeley version2 CSVs matched publisher sizes and SHA-256 values. Actual selected-class inventory: **50 labels, 813 official training rows, 203 official test rows, 1,016 unique normalized clip paths**. Literal labels match the approved selected-class JSON; committed app label map exactly matches that sorted mapping. No signer IDs are available in those CSVs.

External inventory: `~/KumpasBuilds/holistic-migration-data/selected-source-inventory.json`, SHA-256 `23697b80445fe1daedd9dfb1d1127e02e1a474eb13144ff5fcad9e4d589701ca`. Its status is explicitly metadata-only while the original-video archive downloads. Byte/pixel duplicate grouping, decode success, extraction coverage, fit-only observability and new model performance remain unverified.

## Migration decision

Prepare the plan's hands+upper-pose153-feature candidate with explicit masks and shared pure NumPy preprocessing. Preserve raw face observations for possible face-enabled follow-up, but do not claim face is linguistically unnecessary. Treat the30-row length and capture policy as candidate settings pending fit-only feasibility. Do not train a full run until source bytes, feature/capture feasibility and a real tiny-overfit checkpoint are verified. Do not close PRD, expert, live or phone gates from code tests.
