# Data readiness — recovered original FSL-105 sources

## Verdict

**Original videos are available and technically ready for a separately verified re-extraction pipeline.** This does not approve full training, prove signer independence, or close feature/capture/live gates.

The original cloud folders remain untouched. All recovery outputs are outside Git under `~/KumpasBuilds/holistic-migration-data`.

## Executed checks

- Official Mendeley version2 CSVs and archive matched publisher sizes and SHA-256 values. Dataset DOI: `10.17632/48y2y99mb9.2`; the official page displayed CC BY4.0.
- The recovered archive is379,081,783bytes; SHA-256 `c048c0820be1621101dfedeabb76a9fbfca76ed2868eebe23b4cb90d5c748463`. Exact HTTP ranges accelerated a slow partial download; the complete assembled archive was independently reopened and rehashed. Incomplete earlier downloads were retained, not used as complete sources.
- All1,016 selected MOV members were read through ZIP CRC checks and byte-hashed. There are1,016 distinct video-byte hashes and no exact raw-byte duplicate groups.
- All1,016 selected videos were staged with verified bytes under `clips_raw/clips/<original-id>/<filename>.MOV` and fully decoded with OpenCV5.0.0. **1,016 succeeded; zero decode errors.** Actual decoded frame counts matched declared frame counts.
- All videos decode to640×360 BGR at60fps. Total decoded frames:247,622. Counts by clip length:33clips with242frames,268with243,664with244,50with245,1with246.
- Full ordered decoded pixels were SHA-256 hashed with frame-shape headers. **Zero exact decoded-pixel duplicate groups**, including zero cross-label or cross-official-split groups. This is exact-pixel duplicate coverage, not semantic/near-duplicate or signer detection.
- The exact approved class map contains50 labels. Literal CSV labels agree with the selected-class JSON, and the committed app map agrees with ascending original-ID dense mapping. Dense25 remains original49/TODAY.
- Official selected membership is813training /203test clips. Training support is14–17clips per class; test support is4–5. A pre-diagnostic candidate split freezes663fit /150validation /203test, with all50classes in every partition and no original test source admitted to fitting.

## Evidence

External to Git:
- `vendor-file-metadata.json`, `csv-download-receipt.json`, `archive-range-download-receipt.json`.
- `verified-video-byte-inventory.json`: SHA-256 `0ff0c09c7df877c860258049427243aacc03d5f35ef11526715366f28940d41e`.
- `decoded-source-audit-v1/records.jsonl`: SHA-256 `a1926b7f0d3ecc7788db4126fd435a287c867519e642ff9770aeddcc74f63e3b`.
- `decoded-source-audit-v1/summary.json`: complete counts and duplicate groups; actual four-worker decode/hash duration89.010935seconds. This is an audit runtime, not a model benchmark.
- `candidate-partitions-v1.json`: SHA-256 `a80620494894701c9f4f2dfde5a3050f4f80b5532b04004c0761c7945300275f`.

The pre-diagnostic manifest's original text still says decoded-duplicate verification was pending at creation. It remains historically unchanged; the later source audit supplies that completed evidence separately, not by rewriting the frozen membership receipt.

## What remains

1. Accept the corrected shared feature/detector implementation after independent re-review. Its initial review identified a reproduced semantic-array input-validation defect; no full extraction/training is admitted under the rejected snapshot.
2. Freeze observable capture eligibility/rate/duration from fit-only diagnostics and a visible built-in Mac preview. Three earlier fit-only clips support feasibility but not all-gesture coverage.
3. Re-extract every gesture with source/configuration/detector/contract binding, strict missingness and fresh tracker state per clip.
4. Require eligible support for every class, real-source tiny-overfit proof and validation-only selection before full training/evaluation.
5. Continue disclosing unknown signers and prior test exposure. Exact duplicate checks do not establish independent people or an untouched final test.
6. Re-record only if actual quality/coverage or webcam domain checks require it, with explicit recording/storage permission. Do not collect participant data or use a phone.
