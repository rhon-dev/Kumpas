# Evaluation-v1 selection and classifier provenance — 2026-09-30

**Decision: do not replace the app classifier.** The validation-selected checkpoint has been frozen and exported as an offline candidate, but its exploratory reused-test score is below the project's ≥90% numeric gate. The actual app/emulator APK still contains a different, historical model. This is *not* a newly passed final evaluation, a signer-independent result, or a live-camera/physical-device result.

## Selection, before test inspection

- Protocol: `../kumpas-data/sequences/evaluation-v1/manifest.json`, SHA-256 `77cc0cdd49cd9bb29a3c6172ff96eb30050c8fae9fadba02459dd22eeecbef99`; 663 original fit clips, 150 original validation clips, 1,989 **fit-only** augmentations. Original test split retains 203 clips. Signer identities are not supplied.
- `training/models/protocol_experiments_log.json` records two local TensorFlow 2.19.0, seed-20260705 runs. Both attained **0.9600 validation accuracy on 150 original clips**. Baseline (`20260930_153819_protocol_v1_no_face_baseline`, CNN 64/128, LSTM 128/64) had validation macro-F1 **0.9592**; wider (`20260930_154059_protocol_v1_no_face_wider`, LSTM 256/128) had **0.9580**. The predetermined validation accuracy/macro-F1 tie-break chose baseline, without the test score.
- Frozen record: `training/models/protocol_selection_evaluation_v1.json`, SHA-256 `512f9eb32321d1b24b9d40cb5b5cafff8fda99281c9868832a0029a51922be1c`. Selected checkpoint: `../kumpas-data/models/20260930_153819_protocol_v1_no_face_baseline.keras`, SHA-256 `55ba7bb86dab621ea85112073e805818b7f5f417ed6dd9e116db92fe8d61288d`. The selection record checks the protocol and checkpoint digests. These large data/model artifacts are adjacent to the repository, not tracked in Git.

## Evaluation after freeze — exploratory reused test

`training/models/reports/20260930_protocol_v1_no_face/evaluation.{json,md}` report the frozen Keras checkpoint, including per-class metrics: **181/203 = 89.16%**, macro-F1 **0.8852**, Wilson 95% interval **84.14–92.73%**. The point estimate fails the ≥90% gate; the interval is *not* evidence that the gate passed. This is a reused historical test split, previously consulted by four older variants, not an untouched final test. Original-clip grouping does not imply signer independence.

| Numeral | Validation correct / total | Frozen Keras reused-test correct / total | Exported TFLite reused-test correct / total |
|---|---:|---:|---:|
| ONE | 3/3 | 4/4 | 3/4 |
| TWO | 2/3 | 4/4 | 4/4 |
| THREE | 2/3 | 1/4 | 1/4 |
| FOUR | 2/3 | 2/4 | 2/4 |
| **FIVE** | **3/3** | **2/4** | **2/4** |

FIVE's two Keras/TFLite misses are **one THREE and one FOUR**. The older *exploratory* model scored FIVE **1/4** (three predicted FOUR); the improvement on this tiny, reused four-clip subset does not establish robust FIVE recognition. THREE is now also especially weak. Numeral anatomy/left-right correctness is not independently labeled or verified.

## Candidate checkpoint → TFLite, without deployment

`training/tflite_export/export_frozen.py` verifies the selection/checkpoint/protocol and label-map SHA-256 digests before conversion, freezes the fixed `[1,30,258]` concrete function, restricts conversion to TFLite built-in ops with dynamic-range optimization, and compares interpreter and Keras output on the 150 validation clips. The frozen export is at `../kumpas-data/tflite/evaluation-v1-candidate/kumpas_50sign_20260930_153819_protocol_v1_no_face_baseline_builtins_dynamic.tflite`; SHA-256 **`9d8a8035fc0085ca4bd95f3d3fdc9d2f3a9e6439b89789c64305f908536b0468`**. `provenance.json` sits beside it. Its class map matches the app asset: SHA-256 **`4fff4f4bf4df480d257a04f4d125fca5fc2c3c1f3c86970857fb815f239fffb0`**. On validation the candidate has **0/150 top-1 disagreements** from Keras but a **0.18057 maximum absolute probability difference**. On the previously consulted test it has **177/203 = 87.19%**, with four top-1 differences from Keras (all four had been correct in Keras). This exported candidate is **not deployed**.

The actual `app/android/app/src/main/assets/kumpas_50sign.tflite` is SHA-256 **`1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`**, identical to `../kumpas-data/tflite/kumpas_50sign_builtins_dynamic.tflite` specified by `app/fetch_assets.sh`, **not** to the newly selected candidate. The built debug APK's embedded `assets/kumpas_50sign.tflite` has the same SHA-256. On the running emulator, `pm path` identified the installed `base.apk`; its whole-file SHA-256 **`34698508d4931ea201fdd61c5b7b1eae9d0e00e5fd49f62f05d9e41b4642e0ee`** matches the locally inspected debug APK. Host-side predictions of the historical Keras checkpoint and this app TFLite agree on **203/203** reused-test clips and both score **193/203**; that is functional correspondence, not a cryptographic old-checkpoint-to-export chain. `training/tflite_export/tflite_export_log.json` lists the 2026-07-05 checkpoint-family export, but does not record the installed builtins file's digest or conversion input digest. **Exact historical checkpoint-to-installed-byte provenance remains unproved.** No physical phone has been tested.

## Reproduction and release blocker

With TensorFlow 2.19.0, scikit-learn 1.9.1, NumPy 2.1.3 in `$HOME/.kumpas-venvs/tf`, run training tests with `$HOME/.kumpas-venvs/tf/bin/python -m unittest discover -s training/tests -p 'test_*.py' -v`; the frozen evaluator command is `$HOME/.kumpas-venvs/tf/bin/python training/models/evaluate_frozen.py --freeze training/models/protocol_selection_evaluation_v1.json --protocol-dir ../kumpas-data/sequences/evaluation-v1 --test-dir ../kumpas-data/sequences --report-dir <new-output-dir>`. The exporter requires `--freeze`, `--protocol-dir`, `--label-map app/android/app/src/main/assets/label_map.json`, and an unused `--output-dir`. Export refuses to overwrite an output directory and never edits the Android asset. Re-running the converter may produce different bytes; verify its digest and numerical comparisons anew rather than assuming deterministic bitwise export.

**Next release decision:** do not advertise the historical 95.07% or the new 89.16% as final app/signer-independent accuracy. A stronger predeclared validation-only experiment and separate, preferably signer-identified untouched assessment are required to close the evaluation gate; verify Android frame-to-feature behavior and full-device performance before claiming learner-facing recognition. Installing this under-threshold candidate would require an explicit exception, app rebuild, and a fresh embedded-APK hash check.
