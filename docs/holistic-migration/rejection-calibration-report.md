# Rejection calibration implementation — synthetic verification

Status: **BLOCKED_NEEDS_CONTEXT — safe vertical-GREEN immutable partial handoff**; parent retains complete independent specification/quality review and every real-data/acceptance gate. Historical files are read-only. No actual video, array, checkpoint inference, training, camera or device execution has been performed by this worker.

Authoritative brief: `rejection-calibration-brief.md`. Owner and protection baseline: external `evidence/rejection-calibration-public-v1/{owner-authorization,baseline}.json`. Starting HEAD/branch verified `3b1f1d8efa29d1e717833f3869c77872e4df021c` / `holistic-migration`; pre-existing parent changes preserved.

Evidence root: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/rejection-calibration-public-v1/worker`.

Each `NN-name-{red,green}/receipt.json` retains exact command, exit, current source/test SHA-256 bindings, JUnit suite counters and serialized testcase count; `console.log` retains all warnings and failures, `junit.xml` preserves individual cases. The runner is `worker/run_stage.py`; every invocation uses the approved existing interpreter, `-E -B`, fresh owned basetemp and XML. New test functions use pytest parameterization rather than hidden unittest subtests.

## Incremental behavioral TDD

| Stage | Behavior | RED | GREEN |
|---|---|---|---|
|01 admission|Literal OOV identity, no token repair, known-label exclusion, calibration/challenge metadata firewall, real/synthetic distinction|1 failed assertion, exit1|1 passed, exit0|
|02 probability|Float32-only50 probabilities, exact cutoff, earlier-index tie, invalid/bool/nonfinite values|1 failed assertion, exit1|1 passed, exit0|
|03 sweep|9/10 known and1/20 OOV integer gates, one-count crossings, all boundaries, reject-all, infeasible tradeoffs and empty support denial|1 failed/1 passed, exit1|2 passed, exit0|
|04 protocol|Fresh immutable protocol, current hash/runtime/source/owner bindings, synthetic CLI denial, tamper and residual failure denial|1 failed/1 passed, exit1|2 passed, exit0|

All REDs above reached explicit missing-behavior assertions (not syntax/import harness errors). Intermediate receipts bind their own exact source snapshots, not later source revisions. IDE Pyright uses a different interpreter and reported unresolved pytest/type-inference diagnostics; actual approved interpreter executions above are authoritative. No installs were made.

## Parent source gate

Parent reports the independent codec-only audit completed1114/1114 with0errors but6 blocking duplicate groups (`protocol_admission_blocked=true`, deliberate process exit2). This worker has not executed that producer or real data. Preparation and every consuming protocol validation require `protocol_admission_blocked=false` and exactly0 blockers, before any detector/model admission. No quarantine, relabeling, re-splitting or criteria change is authorized. Actual rejection metrics remain unmeasured; this software task cannot clear that source gate.


## Immutable scope handoff

Owner steering now approves a separately versioned quarantine and asks this implementer to stop at the next safe GREEN. `quarantine-owner-authorization.json` is a parent-owned new scope delta, not an implicit exception to the original immutable brief/baseline. This handoff does not interpret or implement that delta. Original blocked-audit denial remains intact. Parent will snapshot these exact eight postimages and issue a refreshed cohesive brief/baseline before continuation.

**Last focused covering result:21 passed,0 failed,0 skipped,0 subtests,2 Keras DeprecationWarnings, exit0 (12.13s).** This is the complete new three-file pytest suite, not the old migration/original suites. Full migration and original training suites were intentionally not run at the superseded-scope handoff, as directed. No independent final specification/quality review or real-data acceptance is claimed. Warnings are the existing installed Keras `__array__(copy=...)` NumPy compatibility warning during fresh synthetic model save. No package/environment/provider changes or Git writes were made.

The last new behavioral slice (stage15) exposed residual `score-complete.json` being recoverable despite unsuccessful postwrite readback when secondary failure-marker writes also failed. GREEN adds an affirmative score-publication barrier retained until exact saved-score readback succeeds. It covers calibration recovery and challenge healthy controls. Stage14 analogously retains a freeze-publication barrier, with a healthy later-report-failure control preserving an already verified affirmative policy.

### Complete stage receipts

All commands, exact flags, exits, sources, warnings and JUnit details are in each stage's `receipt.json`, `console.log`, `junit.xml`; aggregate is `worker/stage-index.json`. Testcase counts below are serialized pytest cases, not assertions; there are no worker unittest subtests. Historical mixed-suite subtest counts are unmeasured because those suites were not launched. Harness errors:0. Earlier stages have their own source snapshots bound in receipts; only the final covering run binds current six production/test Python postimages.

|Stage|Exit|Actual console summary|Serialized cases|
|---|---:|---|---:|
|01-admission-green|0|1 passed in 0.10s|1|
|01-admission-red|1|1 failed in 0.19s|1|
|02-probability-green|0|1 passed in 0.10s|1|
|02-probability-red|1|1 failed in 0.16s|1|
|03-sweep-green|0|2 passed in 0.09s|2|
|03-sweep-red|1|1 failed, 1 passed in 0.16s|2|
|04-protocol-green|0|2 passed in 0.21s|2|
|04-protocol-red|1|1 failed, 1 passed in 0.12s|2|
|05-extraction-green|0|3 passed in 1.35s|3|
|05-extraction-red|1|1 failed, 2 passed in 0.23s|3|
|06-metrics-green|0|3 passed in 0.16s|3|
|06-metrics-red|1|1 failed, 2 passed in 0.17s|3|
|07-calibration-green|0|1 passed in 1.40s|1|
|07-calibration-red|1|1 failed in 0.16s|1|
|08-challenge-green|0|3 passed in 2.27s|3|
|08-challenge-red|1|2 failed, 1 passed in 1.66s|3|
|09-recovery-green|0|6 passed in 2.01s|6|
|09-recovery-red|1|1 failed, 5 passed in 2.49s|6|
|10-native-green|0|7 passed, 2 warnings in 10.00s|7|
|10-native-red|1|1 failed, 6 passed in 2.75s|7|
|11-source-gate-green|0|7 passed in 0.78s|7|
|11-source-gate-red|1|2 failed, 5 passed in 1.51s|7|
|12-consumer-green|0|8 passed, 2 warnings in 9.05s|8|
|12-consumer-red|1|2 failed, 6 passed, 2 warnings in 10.70s|8|
|13-cli-green|0|9 passed, 2 warnings in 10.35s|9|
|13-cli-red|1|1 failed, 8 passed, 2 warnings in 11.22s|9|
|14-publication-green|0|4 passed in 1.77s|4|
|14-publication-red|1|1 failed, 1 passed in 1.46s|2|
|15-score-publication-green|0|3 passed in 1.61s|3|
|15-score-publication-red|1|1 failed in 1.19s|1|
|handoff-focused-green|0|21 passed, 2 warnings in 12.13s|21|

Stages05–15 add streamed synthetic MJPG/BGR extraction and raw codec/face tensor parity, diagnostic pilot firewall, full class support and missingness, known/OOV extended metrics, fixed-model known membership/saved scoring, feasible/infeasible dispositions, separately gated single challenge extraction/assessment, score-before-report publication, saved-output-only recovery, residual policy/score publication barriers, synthetic-only native50-output ordinary forward/save/reload parity, source-gate-before-frozen-admission checks and real-only public CLI denial. Additional tests that were already GREEN when added are coverage-only, not fabricated behavioral RED: infeasible score retention, missing-face/throw cleanup controls and initial residual-policy marker controls. Stage12 adds actual counterexamples for metrics readback and a missing exclusive challenge-extraction reservation.

### Preserved bytes and handoff manifest

`worker/protection-handoff.json` verifies1811/1811 protected repository files and48/48 protected Phase4 artifacts unchanged, with no mismatches. Exactly the eight authorized new repository paths exist. Parent-owned existing scope/status changes were preserved. The original brief and owner authorization were not rewritten.

The exact eight final postimages, SHA-256 digests, file sizes, copy/readback verification, current HEAD, retained evidence inventory and retention budget are recorded in **`worker/handoff/manifest.json`**. Copies are in `worker/handoff/postimages/` using repository-relative paths. This final report's own exact digest is in that manifest rather than an impossible self-referential table. The manifest is the immutable continuation boundary; do not rebind an old test receipt to changed future source.

### Pending interfaces / known review concerns

- **Quarantine view unimplemented:** the next brief must explicitly bind the newly approved owner decision and exactly5 OOV exclusions plus1 known challenge exclusion, leave145 known validation unchanged and merely flag2 historical fit sources. Current real admission still requires original membership and rejects the original audit with blockers. Historical known challenge still expects original203. No automatic exception or silent dropping exists.
- Broad original/migration regressions and independent complete spec/quality review remain pending. All21 new focused cases pass but do not prove every requirement or every negative schema/path/publication fault.
- Strict schema/adversarial coverage and parent/source decoder recipe/reference admission need complete review under the refreshed protocol. The current implementation binds the accepted model, labels, selection, acceptance and known manifest, but the separate `candidate-contract.json` is not yet explicitly included in the new protocol's frozen map; future continuation must finish that feature-contract binding rather than claim it was verified here.
- The current report's per-known-class precision/F1 includes accepted OOV false positives in the precision denominator (extended classifier precision); known recall/support remains known-only. Parent must adjudicate/report separate all-known-only versus extended precision/macro-F1 semantics in the refreshed scope. No real metric has been reported from this candidate.
- Bundle readers recompute raw-derived tensor/capture/presence and check hashes/membership, but complete adversarial strict-ledger/cardinality schema and bounded raw decompression cases remain pending review. No claim of hostile-writer/crash/power-loss atomicity is made for local exclusive writes.
- The native synthetic model intentionally uses a small fixed50-output softmax graph for adapter/decision parity, not the accepted CNN-LSTM. It proves bounded ordinary forward/save/reload behavior only; classifier fitting, source inference, idle safety, signer/linguistic/device acceptance and live readiness remain unmeasured or false.

**Disposition: BLOCKED_NEEDS_CONTEXT (owner-directed scope handoff, not a product failure).** No real extraction/calibration/challenge was run; no real qualifying companion or target outcome exists. Continue only from a refreshed parent brief/baseline and independent review/acceptance gates.
