# Phase 3 — Face-inclusive data status

## Current disposition

The owner approved the full-face contract, tests, then data rebuilding on November 16, 2026. The additive hm1588-v1 software passed complete independent specification and quality review, followed by parent binding adjudication. The actual fit-only diagnostic and full deterministic raw-reuse build completed successfully. Parent independently reconstructed every eligible tensor from the approved equations without calling the new face-feature helpers, and the production consumer reopened the full bundle successfully. The separate six-group campaign review passed specification and evidence quality; parent verified all 1,278 consumed input bindings and accepted bounded face-inclusive dataset evidence. Acceptance is retained externally at `evidence/face-data-parent-20261116/dataset-acceptance.json` under the data root. This closes the owner-approved prerequisite and deterministic data-rebuild package, not recording, model, physical or research gates.

No detector re-extraction was necessary: the historical complete Tasks Holistic campaign preserved all face observations in its lossless raw codec. The current-source graph, original-source/decode evidence, exact raw digests, detector/runtime identities and observed face cardinalities were verified before reuse. Historical contracts, arrays and receipts remain unchanged.

## Actual artifacts

- Dataset: `~/KumpasBuilds/holistic-migration-data/hm1588-canonical-bundle-20261116-v1/`.
- Contract: `docs/holistic-migration/FEATURES_FACE.md`, hm1588-v1, Float32 `[N,30,1588]`.
- Full manifest SHA-256: `71c644b4de78f7031f96f7b25b1d5766f18fa611c33ad12f2a40a353b1c6c19a`.
- Evidence: `~/KumpasBuilds/holistic-migration-data/evidence/face-data-parent-20261116/`.
- Per-gesture counts: `per-gesture-counts.csv` in that evidence directory; all 50 literal output labels and original/dense IDs retained.
- Excluded-source review list: `ineligible-recordings.csv`; detailed missing observations: `missing-face-observations.csv`.

The bundle contains exact label/ID order, source-level capture and eligibility ledgers, original partition membership, the approved contract copy and hash-bound Float32 arrays. No augmentation, source substitution, new windowing or class reduction was performed.

## Source and eligible denominators

| Partition | Declared original recordings | Eligible tensors | Ineligible recordings | Tensor shape |
|---|---:|---:|---:|---|
| Fit | 663 | 649 | 14 | `[649,30,1588]` |
| Validation | 150 | 145 | 5 | `[145,30,1588]` |
| Test | 203 | 203 | 0 | `[203,30,1588]` |
| Total | 1,016 | 997 | 19 | One tensor per eligible recording |

All 50 classes retain eligible support in every partition. Minimum eligible support per class is 7 fit, 1 validation and 4 test recordings. One validation example for a class is a substantial statistical limitation, not evidence of adequate diversity or learnability. The declared denominators retain all 19 exclusions.

All 19 exclusions have reason `invalid_face`; no rule was relaxed and no missing face was interpolated or removed to bridge a capture. The raw campaign contains 62,027 actual observations: 62,000 present 478-point faces and 27 absent faces across 20 recordings. One recording (`clips/1/10.MOV`) remains eligible because its absent face is outside the existing hand-bounded capture interval. Actual observations and the 30 resampled rows per tensor are different units. Zero exact new-feature duplicate groups were found; this does not establish semantic uniqueness or signer independence.

The 19 excluded recordings are candidates for a separately approved source-quality/replacement decision, not an instruction or permission to collect recordings. Every class remains represented without them. No new webcam video, landmark recording or participant data was collected.

## Executed verification

- Software parent: 113 new cases passed; full migration 602 cases plus 293 subtests passed with 67 dependency warnings; original training 51 cases plus 289 subtests passed with 3 warnings. No failures, errors or skips. These are synthetic software checks.
- Independent software reviewer: 23 focused synthetic cases passed and complete specification/quality PASS. Parent verified all 390 consumed input bindings and all 892 indexed reviewer evidence files. Nonblocking external-probe retention and parent-status wording suggestions were recorded, not silently erased.
- Real fit-only diagnostic: the literal first frozen fit source for each class, 50/50 eligible, 3,057 actual observations. Exact IDs were frozen before new-feature preparation; 966 nonselected sources had unmeasured new-contract eligibility at that diagnostic stage. Parent independently matched every diagnostic tensor.
- Real full build: CLI exit 0; 18.285647 seconds UTC wall interval and 18.285973792000732 seconds monotonic interval. These are raw-reuse build timings, not detector throughput, model inference latency, camera FPS or physical performance. Pre-launch 600-second timeout, 1 GiB output budget and available disk were recorded.
- Independent full readback: all 1,016 source identities/raw bindings, every capture disposition and all 997 eligible tensors matched independently recomputed finite Float32 numerical values exactly. The retained parent oracle uses `np.array_equal`; it does not establish signed-zero-sensitive byte equality. Partition membership, class order and support/counts reconciled. The production `validate_bundle` readback also passed.
- Independent campaign review: all six groups passed. The reviewer freshly checked every raw digest, all ordered labels/IDs/class support, all 997 historical prefixes, 56 independently reconstructed full face tensors and all 19 exclusions. The 997-prefix and 56-full-tensor checks included byte-sensitive comparisons. The broader complete parent numerical reconstruction remains separately attributed. One nonblocking precision suggestion is resolved by the corrected numerical-equality wording above; historical scripts, receipts and data were not changed. An initial failed reviewer harness attempt remains preserved; corrected audit and supplemental checks exited 0.
- Preservation: all 126 protected source/contract bindings and the eight new accepted software/contract/report inputs matched; historical hm153 bundle manifest and every bound artifact matched its accepted historical digest. Original media was not decoded again.

Detailed commands, exits, source bindings, UTC/monotonic intervals and separate producer/consumer/independent receipts are retained externally. The producer flags remain `training_qualified=false`, `live_ready=false` and `model_evaluated=false`.

## Entry points and stopping boundary

From `~/KumpasBuilds/holistic-migration`, use the existing interpreter with `-E -B` and the approved scratch TMPDIR. `python -m training.holistic_migration.face_dataset --help` documents the additive builder. Any reproduction must use a new absolute external output directory; never reuse or overwrite the completed bundle. The existing full-bundle consumer is `face_dataset.validate_bundle(Path(...))`; independent mathematical readback is retained at `evidence/face-data-resume-20261116/independent_tensor_readback.py` under the external data root.

The existing trainer/evaluator are still 153-specific and cannot consume this new contract. Do not run them on these tensors. Actual-source tiny/full fitting, classifier scoring, rejection calibration, export or activation require a separate model-phase decision and compatible, reviewed tooling. No trained candidate was produced by Phase 3.

Signer IDs remain unknown, official test sources were historically exposed, and no separately annotated idle/outside-vocabulary negatives exist here. Facial feature inclusion is not expert linguistic validation. Owner overlay/physical-left-right confirmation, live recognition, new recording/storage permission, phone work and participant/research acceptance remain open or excluded. This is bounded data engineering evidence only.
