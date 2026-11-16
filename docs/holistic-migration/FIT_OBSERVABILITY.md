# All-class fit-only observability pilot

## Scope

Before this diagnostic, the candidate partition membership and50 clip identities were saved in a new config. Exactly one existing fit clip per approved class was selected, in dense index order, without classifier predictions. No validation/test detector or classifier inference was performed by this pilot. It is not the final extraction campaign or a training/evaluation result.

The accepted Task A source hashes were verified before and after execution. Each source MOV matched the previously verified original-byte inventory. A fresh Tasks Holistic detector was constructed and closed for each clip. Every fourth original frame was processed; this is a declared stride4 pilot setting, not a frozen live policy.

## Executed results

- **50/50 sources succeeded**, covering all50 approved classes; zero detector/packing errors.
- **3,057 actual observations** were produced. Every observation had usable shoulder/pose under the candidate contract.
- Every class's selected clip produced hand observations; the minimum was14. The minimum longest usable-pose run was61observations.
- Observed nonempty face output count was478, not the legacy468.
- Actual elapsed time with three concurrent clip jobs was96.1031595seconds. This is a dataset diagnostic runtime, not live camera FPS or a guaranteed full-run estimate.
- Each output retains timestamps, raw pose/hands/face and explicit component presence separately from the computed153-feature rows. Raw values/zero-filled missing slots are not human gesture annotations.

## Exact evidence

External campaign directory:
`~/KumpasBuilds/holistic-migration-data/fit-observability-50-9f366e01d2154594b7f45ef624d8ebf4/`

- `config.json` SHA-256: `74d7c85b9c43a107a79090b2afec2ab08b470f209f9fe10b210d75ad453649e7`.
- `records.jsonl` SHA-256: `b3aa4c7c600cf00af70bf42e81b872e756d9bcc674f04fb814718ef006e84696`.
- `summary.json` contains counts and explicit empty failure lists.
- Fifty NPZ paths/digests are recorded per source; native runtime warnings are retained in `native-stderr.log`, not hidden as a warning-free run.

## Limits and next gate

SDK component presence is not independently annotated sign activity, detector recall, anatomical handedness or sign correctness. One source per class cannot establish full-clip eligibility across the corpus or sufficiency of dropping classifier face features. No class probabilities, loss, accuracy or model-selection results exist from this run.

These observations support continuing candidate capture/sequence feasibility work without requiring universal re-recording first. They do not authorize silently copying pilot files into a final dataset: the new extraction runner must bind its own source/configuration/runtime/contract receipts and verify any deliberate cache reuse. Visible Mac tracking, exact temporal/capture policy, complete re-extraction, actual tiny-overfit, all-gesture fitting, rejection evaluation and owner-performed acceptance remain open.
