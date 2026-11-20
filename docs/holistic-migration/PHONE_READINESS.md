# Phase 6 — Phone readiness plan

**Planning deliverable, November 17, 2026. Phone entry is BLOCKED.** The owner's `start phase 6` authorizes this documentation, not conversion, SDK/build/device work or mobile integration. This is **Holistic Migration Phase 6**, not the PRD Phase 6 corrective-feedback engine. Target remains the governed Android thesis app; the separate iOS prototype and the owner's iPhone are not substitute targets.

No conversion, classifier/detector inference, camera launch, phone query, SDK installation/build, app/asset change, participant processing, activation or Git publication occurred in this package. Existing dirty/untracked work is preserved. `PROGRESS.md` retains historical chronology; its old active-worker wording is not a live-worker assertion. No workers were live at this package's prerequisite check. Interrupted rejection preparation is neither restarted nor accepted by this phase.

## 1. Evidence and candidate identity

Repository: `~/KumpasBuilds/holistic-migration`, branch `holistic-migration`, HEAD `3b1f1d8efa29d1e717833f3869c77872e4df021c`. External root below is `~/KumpasBuilds/holistic-migration-data`.

Fresh read-only binding evidence: external `evidence/phase-6-planning-20261117/{baseline,candidate-inventory,verification}.json`; verification is published after scope checks. These checks read artifact/configuration bytes without loading TensorFlow, MediaPipe or Android. The first collector confused canonical-JSON and file-byte class hashes and stopped before project edits; the corrected collector verifies both domains independently. This was an evidence-harness error, not changed labels or a model failure.

| Item | Exact bound reference | Meaning / limit |
|---|---|---|
| Classifier | `evidence/phase-4-20261116/full-source-v1/model.keras` | 6,379,907 bytes, Keras archive; **not** TFLite size or inference RAM |
| Classifier SHA-256 | `ea50489a27353cbf4f4e9b53b1a6252fa7c5c6a9f0021660347f7dcc1b1cda47` | Frozen all-50 checkpoint, selected epoch 54; no refitting |
| Feature contract | `docs/holistic-migration/FEATURES_FACE.md`, SHA-256 `f0c8021bd0ca8a227aa84169991345672966faa3648e75e0a62ea27155362c45` | `hm1588-v1`; historical hm153 and app258 are incompatible |
| Data manifest | `hm1588-canonical-bundle-20261116-v1/data_manifest.json`, SHA-256 `71c644b4de78f7031f96f7b25b1d5766f18fa611c33ad12f2a40a353b1c6c19a` | Retains 1,016 declared / 997 eligible / 19 invalid_face exclusions |
| Exact label-file bytes | Bundle `class_metadata.json`, SHA-256 `b634bdeb19b2fbf7482bdd46f791f16725d6510275e5d552f29f3bfc7c628eb6` | JSON file bytes; do not confuse with next identity |
| Ordered classes canonical digest | `bde14b3ed48b33158b64f3cac51f0147b8846db8de094bad8daeeeda6a4a188d` | SHA-256 of UTF-8 JSON, sorted keys, no spaces, ensure_ascii=false, finite values; complete objects include category |
| Historical policy | `full-source-v1/policy.json`, SHA-256 `cfc992711743499f0d48eef01e44b17f14fe1173edce0a9728ee8cade067e035` | `closed_set_argmax`, 50 outputs, `live_ready=false`; unknown rejection unmeasured |
| Detector | `holistic_landmarker.task`, 13,683,609 bytes, SHA-256 `e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8` | Official float16/version1 bundle, recorded download identity, **not a vendor-published checksum** |
| Runtime basis | Tasks Holistic VIDEO / CPU; Python 3.11.15, MediaPipe 1.2.0; TF 2.19.0 / Keras 3.15.1 | Existing Mac execution basis, not verified Android runtime compatibility |

Prior accepted offline execution and limits are in `PHASE_3_STATUS.md`, `PHASE_4_STATUS.md` and external `all50-campaign-v1/phase4-offline-acceptance.json`. The 193/203 reused-test result is exploratory, not an untouched/signer-independent result. SON and GRANDFATHER each remain 2/4; six other test classes are 3/4. Validation BLUE is 1/3. No aggregate metric waives these weaknesses. The quarantine view documents conflicting publisher labels, flags two historical fit sources and excludes one historical known challenge source only from new scoring; it does not rewrite this trained model or its historical results.

## 2. Future export contract — not an exported artifact

- Export a separate **Float32 reference** with fixed input **`[1,30,1588]`**, dtype Float32; output **`[1,50]`**, Float32 softmax probabilities. Current saved Keras config is `[null,30,1588]`; fixed batch1 is a future serving wrapper, not an existing static signature. Inference mode only, Dropout disabled, frozen BatchNorm moments, stateless attempts; never use batch-mode serving or carry LSTM state across attempts.
- First 153 features are the accepted left hand63 / right hand63 / pose11–16 XYZ+visibility24 / three masks. Face indices0–477 XYZ append at153:1587, face mask1587. Preserve exact SDK order, SDK-left/right slots, Float64 normalization then Float32 packing, shoulder-midpoint XY/shoulder-width scaling, wrist-local hand Z, shoulder-local pose Z and separate mean-relative face Z. Pose shoulder visibility >=0.5 and width >=0.0001. Visibility/masks are not centered/scaled; absent hand blocks remain zero. Do not reuse hip/torso app normalization.
- Preserve unmirrored640×360 RGB detector input, 15Hz actual timestamps, VIDEO session isolation, strict increasing integer milliseconds, nearest-observation30-row sampling with earlier tie-breaking. Hands bound the interval. Require >=8 observations / >=4 hand-present, 400–5000ms inclusive, gaps <=250ms, usable shoulders and exact478-point face throughout. Do not delete invalid internal rows, bridge gaps, invent points or interpolate absent hands. Preserve reason precedence from `FEATURES_FACE.md`.
- All50 label strings/IDs below are literal; dense output index is **not** original ID. No51st output, punctuation normalization, automatic sorting by display name or aliasing.
- Keep historical closed-set policy immutable. It has no safety threshold. A future accepted rejection companion must bind model, ordered labels, feature contract, exact threshold/operator and comparison semantics, validation membership and scores, source/quarantine view, feasibility proof and its own digest. Until accepted, phone entry remains blocked; no default confidence threshold, no claim that argmax is safe acceptance. Calibration and idle evidence cannot be supplied by export parity.
- Future bundle manifest must bind `.tflite` bytes/signature, source checkpoint, converter/runtime/operator versions, labels, preprocessing/capture code, detector graph/bundle/options, policy, parity receipts and rollback inventory. Unknown/mismatched identities or failed/incomplete publication must fail closed before invocation; no default assets. Write only to a fresh exclusive external experiment directory until separately approved activation.

### Literal output ordering

| Dense | Original | Label |
|---:|---:|---|
| 0 | 0 | GOOD MORNING |
| 1 | 1 | GOOD AFTERNOON |
| 2 | 2 | GOOD EVENING |
| 3 | 3 | HELLO |
| 4 | 4 | HOW ARE YOU |
| 5 | 5 | IM FINE |
| 6 | 6 | NICE TO MEET YOU |
| 7 | 7 | THANK YOU |
| 8 | 8 | YOURE WELCOME |
| 9 | 9 | SEE YOU TOMORROW |
| 10 | 10 | UNDERSTAND |
| 11 | 11 | DON’T UNDERSTAND |
| 12 | 12 | KNOW |
| 13 | 13 | DON’T KNOW |
| 14 | 14 | NO |
| 15 | 15 | YES |
| 16 | 16 | WRONG |
| 17 | 17 | CORRECT |
| 18 | 18 | SLOW |
| 19 | 19 | FAST |
| 20 | 20 | ONE |
| 21 | 21 | TWO |
| 22 | 22 | THREE |
| 23 | 23 | FOUR |
| 24 | 24 | FIVE |
| 25 | 49 | TODAY |
| 26 | 50 | TOMORROW |
| 27 | 51 | YESTERDAY |
| 28 | 52 | FATHER |
| 29 | 53 | MOTHER |
| 30 | 54 | SON |
| 31 | 55 | DAUGHTER |
| 32 | 56 | GRANDFATHER |
| 33 | 57 | GRANDMOTHER |
| 34 | 62 | BOY |
| 35 | 63 | GIRL |
| 36 | 64 | MAN |
| 37 | 65 | WOMAN |
| 38 | 66 | DEAF |
| 39 | 67 | HARD OF HEARING |
| 40 | 72 | BLUE |
| 41 | 74 | RED |
| 42 | 76 | BLACK |
| 43 | 77 | WHITE |
| 44 | 85 | BREAD |
| 45 | 86 | EGG |
| 46 | 89 | CHICKEN |
| 47 | 91 | RICE |
| 48 | 95 | HOT |
| 49 | 96 | COLD |

## 3. Operator / detector compatibility investigation

**Source-level investigation completed; exact artifact conversion and SDK capability remain UNVERIFIED.** The reviewed classifier contains Conv1D64/128, BatchNorm, MaxPool2, LSTM128/64, Dense128/50 and Dropout. Google documents standard Keras LSTM conversion to fused LiteRT LSTM operations [1]; that is not proof this TF2.19/Keras3.15.1 checkpoint lowers successfully. Future approved host check must bind a batch1 inference signature, require built-in operators only first, retain the full converter log, inspect every emitted operator/version and tensor signature, then execute the artifact on the exact intended runtime. Inspect TensorList/dynamic-shape lowering if conversion fails; stop rather than alter topology/weights or silently enable Flex/custom ops.

The historical `training/tflite_export/export_tflite.py:30–41,75–98` enables built-ins **plus SELECT_TF_OPS**, turns on default optimization and emits dynamic/float16 candidates, copies labels from a historical sequence path and appends a repository log. It supplies neither this fixed Float32 reference nor candidate-bound labels/parity. **Do not run it for hm1588.** Google notes SELECT_TF_OPS needs matching runtime support and adds runtime binary cost [2]. A Python TF interpreter can conceal a missing Android Flex runtime. Any Flex fallback requires a separate dependency/size/delegate decision, not automatic acceptance.

Current read-only Android references pin `tasks-vision:0.10.14`, LiteRT `1.1.2`, CameraX `1.4.1`, minSdk24; compileSdk/targetSdk/NDK are Flutter-derived, not numerically resolved here. `VisionEngine.kt:17–27,50–63` still uses separate Pose/Hands, 258 features and frame-stride sampling; `FeatureNormalizer.kt` uses hip/torso normalization. `FeedbackEngine.kt` and gold-standard loading also assume258. This is **not** a model-file drop-in; future feedback/reference compatibility needs separate design approval. Leave it untouched.

The current official Java API documents `HolisticLandmarker`, a pre-trained bundle, VIDEO `detectForVideo`, monotonically increasing millisecond timestamps and explicit image-processing/rotation options [4]. This disproves a blanket claim that no Java Holistic API exists, but does not prove it exists in the pinned0.10.14 AAR, supports this bundle or matches Python1.2.0. A separately authorized host-only SDK check must resolve exact AAR/ABI/API/native graph symbols, bundle loading/options, face478 output, visibility/hand slots and runtime execution evidence. Headers/API pages alone do not qualify it. Preserve VIDEO semantics; a switch to async LIVE_STREAM/drop policy, separate detectors or another model bundle needs versioned parity and approval. No SDK fetch, Gradle resolution or native build is part of this phase.

### Quantization follows Float32, never replaces its reference

Google's retrieved post-training page now warns that conversion-time quantization is deprecated and recommends Float32 conversion followed by LiteRT Quantizer [3]. The existing pinned TF2.19 pipeline predates that guidance. Record this tooling decision gate; **do not upgrade packages** here. Later decide between a separately verified pinned historical path and an approved new quantizer environment, each with exact versions and reproducibility receipts. Documentation availability does not select a toolchain.

Future float16/dynamic-range/int8 candidates get independent hashes and parity/calibration gates. Weight compression is not measured RAM/latency reduction. Representative activation data must be declared fit-only, capture/mask-preserving and contain no final/challenge data. No invented random arrays as representative sign data. Check supported recurrent kernels, input/output scales and zero-points, per-tensor/per-axis behavior, saturation, mask zeros/ones and dequantization. A changed probability distribution requires a new validation-only rejection companion; never copy a Float32 threshold without verification or tune on exposed test/challenge outcomes. No quantization-aware retraining is authorized.

## 4. Future parity protocol — proposed, not executed or approved tolerances

Freeze input fixture membership/digests and numeric criteria **before** conversion/scoring. Preserve failures rather than widening tolerances after seeing results. Proposed Float32 criteria: feature absolute error <=1e-6 with rtol0 on identical raw observations (masks/timestamps/indices exact); probability elementwise absolute error <=1e-5 plus relative tolerance1e-4; finite outputs, sum within1e-5 of1, exact top1 and exact policy decision on every declared eligible fixture. Owner/reviewer agreement remains required. Quantized criteria require separate preapproval; there is no accepted mismatch allowance.

| Layer | Fixture / comparison | Required report / stop |
|---|---|---|
| Preprocessing | Same recorded raw pose/hands/face/timestamps through Python and future Android packer/resampler | Compare every Float32 value and mask; missing hand/face, bad shoulders, low visibility, nearest ties, duration/gap edges, malformed/overflow and invalid-capture reason controls. No classifier call for invalid inputs |
| Float32 classifier | Exact singleton tensors, same saved Keras inference and exported CPU runtime | Freeze all145 eligible validation IDs/50-class support and source/exclusion membership; retain all150 declared known-validation sources including five exclusions. Repeated/singleton/batch-order controls, all50 probabilities, max/mean deltas, exact top1, margin/tie cases and per-class mismatch counts |
| Rejection | Future accepted policy on identical Keras/TFLite probabilities | Exact comparison operator/dtype/tie behavior; synthetic below/equal/above threshold and near-boundary controls; eligible accepted/rejected/error outcomes agree. Missing calibrated policy blocks safety parity; historical argmax checks are diagnostic only |
| Negative validation | Separately accepted quarantine-aware calibration membership only | Retain all declarations, quarantine/eligibility reasons and class support. Exact reference/conversion FAR and correct-known acceptance, including per-class effects. No challenge-based selection or hidden exclusions |
| Native detector | Identical decoded unmirrored frames and timestamps, new tracker per clip | Bind detector/runtime/graph/options, colors, rotation and sampling. Compare anatomy/slots, face cardinality, tracking history/missingness separately. Nonidentical detectors are not normalized-feature parity fixtures |
| Quantized candidate | Same frozen fixtures plus fit-only activation calibration receipts | Dequantized probability and top1/rejection/per-class deltas and saturation; independent policy feasibility. A passing Float32 export cannot qualify this row |
| Robustness / package | Bad shape/dtype, reordered labels, missing/mismatched assets, init/cancel/restart/cleanup faults | Reject before prediction, preserve primaries/owned resources, no asset substitution. Require exact package readback after any separately approved activation |

Classifier parity consumes precomputed tensors; it does not package Holistic, prove camera alignment or measure detection accuracy. The same-frame detector path and shared-raw feature path are different experiments. Use all source/eligible denominators; retain known label ambiguity, unknown signers and historic test exposure. Reused test predictions may be reported only under a separately frozen exploratory protocol, never to choose exporter/delegate/threshold settings. Host replay is not device acceptance.

## 5. Cost accounting and proposed phone budgets

All values below are separate accounting lines. Byte arithmetic is computed in `candidate-inventory.json`; no phone timing/memory was measured. MiB means1,048,576 bytes.

| Component | Known bytes / proposed ceiling | Acceptance meaning |
|---|---|---|
| Keras checkpoint archive | 6,379,907 measured bytes | Serialization can include training/optimizer state; not weight-only or TFLite estimate |
| Float32 classifier `.tflite` | Size unmeasured; proposed <=8MiB | Exact future artifact measurement required, not a promise |
| Holistic detector `.task` | 13,683,609 measured bytes; proposed <=16MiB asset budget | Bundle bytes only, not native SDK/APK or loaded memory |
| Detector and classifier native libraries | Size unmeasured; proposed incremental packaged payload <=40MiB for agreed ABIs | Report uncompressed libraries and APK contribution separately; any Flex cost is separate |
| Classifier input / output | 190,560 / 200 exact Float32 bytes | Excludes interpreter arena, intermediates, tensors, copies and delegate buffers |
| Detector input frame | 691,200 bytes RGB640×360 | Excludes original camera planes, stride padding and resize temporaries |
| Historical Mac ingress example | 3,686,400 bytes BGRA1280×720 | Not a chosen phone capture format or phone measurement |
| Total app peak memory | Unmeasured; proposed <=256MiB incremental over camera-off idle | On agreed4GB physical Android target; report total/delta Java/native/graphics/PSS and peak, queues, arena/delegates separately |
| Classifier service time | Unmeasured; existing PRD target <150ms; proposed use p95 after warmup | Fixed1×30×1588, include binding/copy/invoke/read; also report invoke-only and cold load separately |
| Preview throughput | Unmeasured; PRD24–30FPS video-pipeline target | Count camera delivered, analyzed, detector processed and display observations separately; no inference-event-as-camera-FPS substitution |
| Detector observation service | Unmeasured; proposed15Hz, p95 <=66.7ms at640×360 | This is the capture contract cadence, not a silent reduction of the PRD24–30FPS pipeline target; missed/gap/invalid attempts stay visible |
| End-to-end decision | Unmeasured; proposed p95 <=300ms from final observation to delivered decision | Separately measure detector completion, feature/queue/copy/classifier/policy/UI stages. Do not sum unrelated stage percentiles to invent end-to-end p95 |
| Sustained run | Unmeasured; proposed >=10minutes with no crash and no below-target sustained segment | Report full trace plus per-minute throughput/p95, peak RAM, drops, thermal status/battery; cold and thermally steady behavior differ |

These ceilings and phone percentile definitions are **proposed and require owner agreement**; the historical PRD targets remain recorded, not newly passed or silently amended. Mac15FPS/300ms targets and the39.68-second tracking-only session do not establish phone performance. Detector+classifier scheduling, async queues and UI can dominate; face computation remains present even when blendshape/segmentation outputs are disabled. Do not subtract detector cost by assuming unused landmarks are free. GPU/CPU/NNAPI or other delegates require explicit version/device-supported paths, numerical parity and sustained profiling; a delegate toggle alone is not acceleration evidence.

## 6. Phone-entry checklist and decision sequence

| Gate | Current state | Evidence or required next action |
|---|---|---|
| Published source audit and exact50-label mapping | Complete within isolated snapshot | `CURRENT_STATE_AUDIT.md`; all50 rows freshly bound here. Unpublished cloud work and historical binary lineage are not newly certified |
| Data provenance and splits documented | Bounded accepted with limitations | Phase3 receipts; 19 exclusions, unknown signers, exposed test, public-label ambiguity/quarantine retained; no new signer-independent claim |
| Offline all-gesture model and metrics | Bounded offline accepted, not all-gesture acceptance | Phase4 reports; weak classes retained. Aggregate95.07% is not per-gesture/live acceptance |
| Rejection companion and true idle evidence | OPEN / BLOCKING | `REJECTION_STATUS.md`; unfinished, unaccepted calibration; no accepted threshold. True idle is not public OOV footage |
| Owner-performed Mac recognition and anatomy | OPEN / BLOCKING | Phase5 all50×two-condition trials, physical left/right, >=9/10 each, idle5min, <=1/20 OOV,10min FPS/latency/crash and offline/live replay proof absent here. Computer access or a tracking preview is not ground truth |
| Frozen candidate, preprocessing, detector, labels and policy | Historical identities bound; deployment freeze OPEN | Candidate-inventory verifies current references; final calibrated policy and complete independently read-back rollback bundle required before phone entry |
| Exact target SDK/API/ABI/bundle support | OPEN / separately approved host check | Section3; current web API is not pinned-AAR capability, package link or runtime proof |
| Physical Android device and budget agreement | OPEN | Name actual device/SoC/RAM/OS/API/camera conditions and approved budgets; no device queries in planning. No iPhone substitution or emulator-as-physical evidence |
| Governance/expert requirements | OPEN as applicable | PM/adviser signatures, linguistic/anatomical validity and reference/feedback compatibility stay distinct; no research or participant approval inferred |
| Explicit owner approval for phone work | NOT GRANTED | This request approves planning only. Separately authorize exact host check/export, then implementation, then install/device measurement/activation scopes |

### Rollback and later handoff requirements

Before a separately authorized activation, create an exclusive external rollback bundle of the exact current APK/build identity (if available), embedded classifier, detector bundles, labels, preprocessing/capture/policy versions and reference assets. Read back every copy and record cryptographic identities; unknown/unavailable APK or ignored asset remains missing, not reconstructed evidence. Preserve original frozen Keras/data/report artifacts and this planning baseline. Do not overwrite the historical app model, label map, references or exporter log. Roll back the **coherent whole contract**, not just weights; old258 references cannot consume1588 rows. No rollback installation is authorized now, and file copies alone would not prove an installed rollback succeeded.

Next actions, in order:
1. Finish the separately authorized rejection software/review and validation-only experiment, or retain infeasibility. This phase neither resumes nor bypasses it.
2. With fresh owner readiness and separately agreed storage, complete Phase5 recognition/idle/OOV/anatomy/performance gates; no recording permission is implied.
3. Agree phone budgets, target identity and governance gaps. Keep phone entry blocked if any required gate remains unmet.
4. Obtain bounded host-only SDK/export-check authorization. Then verify exact pinned runtime/bundle and built-ins Float32 conversion/parity in exclusive external outputs, with independent review; no app change is implicit.
5. Only with separately approved mobile implementation/installation/activation scope, design shared preprocessing/capture and reference compatibility, build, inspect actual APK assets/ABIs, install and measure a physical target. Never label these future steps executed.

## 7. Official references — retrieved November 17, 2026

Retained HTML/text snapshots and SHA-256 receipts are external `evidence/phase-6-planning-20261117/{rnn,ops-select,quantization,holistic-java}.{html,txt}` and `official-references-parsed.json`. Direct HTTP retrieval succeeded; the optional third-party HTML parser was unavailable, so stdlib HTMLParser extracted the retained pages without installing dependencies. The extraction backend also declined URL extraction; neither failure was treated as project evidence.

- **[1] Google AI Edge, TensorFlow RNN conversion to LiteRT**: `https://ai.google.dev/edge/litert/models/convert/rnn` — standard Keras LSTM/fused-op support is documented; exact-checkpoint conversion still requires execution.
- **[2] Google AI Edge, Select TensorFlow operators**: `https://ai.google.dev/edge/litert/models/ops_select` — Flex/select operations need additional runtime support and affect binary cost; published example sizes are not estimates for Kumpas.
- **[3] Google AI Edge, Post-training quantization**: `https://ai.google.dev/edge/litert/models/post_training_quantization` — Float32 compatibility baseline first; retrieved deprecation warning requires an explicit quantizer/toolchain decision, not a package upgrade here.
- **[4] Google MediaPipe Java HolisticLandmarker reference**: `https://ai.google.dev/edge/mediapipe/api/solutions/java/com/google/mediapipe/tasks/vision/holisticlandmarker/HolisticLandmarker` — API/model/running-mode/timestamp/rotation contract, not certification of the project's pinned Android AAR.

**Disposition:** phone-readiness planning supplied; physical phone readiness, export compatibility and all deployment acceptance remain unverified/open. No mobile work is authorized or executed by this document.

## Sources

[1] https://ai.google.dev/edge/litert/models/convert/rnn
[2] https://ai.google.dev/edge/litert/models/ops_select
[3] https://ai.google.dev/edge/litert/models/post_training_quantization
[4] https://ai.google.dev/edge/mediapipe/api/solutions/java/com/google/mediapipe/tasks/vision/holisticlandmarker/HolisticLandmarker
