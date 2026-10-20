# A3a recovery execution

Host-only synthetic contract work. No installed transport, camera, inference, or physical qualification claim. RED/GREEN commands and XML snapshots recorded by recovery runner.
- `control-red`: exit 1; log `control-red.log`; exact command in ledger.
- `control-green`: exit 1; log `control-green.log`; exact command in ledger.
- `control-green-2`: exit 0; log `control-green-2.log`; exact command in ledger.
- `export-isolation-red`: exit 1; log `export-isolation-red.log`; exact command in ledger.
- `export-isolation-green`: exit 1; log `export-isolation-green.log`; exact command in ledger.
- `export-isolation-green-2`: exit 0; log `export-isolation-green-2.log`; exact command in ledger.
- `artifact-contract-red`: exit 1; log `artifact-contract-red.log`; exact command in ledger.
- `producer-path-red`: exit 1; log `producer-path-red.log`; exact command in ledger.
- `producer-first-execution`: exit 0; log `producer-first-execution.log`; exact command in ledger.
- `focused-final`: exit 0; log `focused-final.log`; exact command in ledger.
- `focused-handoff`: exit 0; log `focused-handoff.log`; exact command in ledger.
- `explicit-handoff`: exit 0; log `explicit-handoff.log`; exact command in ledger.
- `full-handoff`: exit 0; log `full-handoff.log`; exact command in ledger.
- `focused-handoff-2`: exit 0; log `focused-handoff-2.log`; exact command in ledger.
- `explicit-handoff-2`: exit 0; log `explicit-handoff-2.log`; exact command in ledger.
- `full-handoff-2`: exit 0; log `full-handoff-2.log`; exact command in ledger.
- `feedback-schema-red`: exit 1; log `feedback-schema-red.log`; exact command in ledger.
- `focused-handoff-3`: exit 0; log `focused-handoff-3.log`; exact command in ledger.
- `explicit-handoff-3`: exit 0; log `explicit-handoff-3.log`; exact command in ledger.
- `full-handoff-3`: exit 0; log `full-handoff-3.log`; exact command in ledger.

## Final outcome — DONE_WITH_CONCERNS (A3a host-only; parent acceptance pending)

- Final consumer candidate ONLY: `handoff-final3-20261016/22ebc4d3-32ee-4bf1-bb54-3708ede613d2/manifest.json`.
- Manifest SHA256 `4bfa51cf5e4c67b304ef86c869326d2d0dd633337e6c3af6cb2a8cf128725c69`; integer TEST schema1; 11 exact artifacts, 42 source hashes verified against precompile ledger and current files; 25 actual controls; real isolated SQLite/export/partial purge/retry/reopen.
- `focused-handoff-3`: 129 tests. `explicit-handoff-3`: 5 tests. `full-handoff-3`: 170 tests plus freshly executed instrumentation Kotlin source compile. All final tests have zero failures/errors/skips. XML snapshots and exact commands/exits are in this directory/ledger. Both full target tasks executed, not UP-TO-DATE.
- All82 protected hashes and8 latest accepted A2a hashes rechecked unchanged. MainActivity/factory changed intentionally; their reconstructed preimages exactly match latest A2b acceptance. See `recovery-final-authorized-delta.diff` and `recovery-final-source-postimages.json`, which supersede the earlier development freezes. Other accepted A2b tests/resources unchanged.
- Three modes retain actual native immutable report bytes; confirmed/unconfirmed retain actual companion bytes; faulted deliberately has NO companion bytes. No payload reconstruction or historical campaign replay script.
- `handoff-interface-v1.md` specifies the envelope, exact filenames, reproduction command, isolation/transport boundaries and superseded outputs. `recovery-final-verification.json` records actual readback results.

### Regression and development failures retained

`control-red` failed the missing callable contract before extraction. `control-green` initially failed the reflective selector under Robolectric; direct callable use corrected that test plumbing, then `control-green-2` passed22. `export-isolation-red` actually returned EXPORT_FAILED rather than reading the explicit fixture DB. Export helper acquisition was bound to the initialization factory; `export-isolation-green` then exposed an unpopulated fixture raw-handle tracker, corrected without changing production behavior; `export-isolation-green-2` passed23. `artifact-contract-red` records missing test-only publisher availability; `producer-path-red` records missing Gradle source-root forwarding. The subsequent helper negative matrix is coverage, not a claimed pre-existing product defect.

Source/consumer review caught a constructed feedback shape incompatible with the existing Dart model. A new assertion inside the producer reproduced it in `feedback-schema-red` BEFORE fixing the synthetic fields. `feedback-schema-red-producer-failure.log` preserves the actual producer stack, and that failed run had no success manifest. Final3 numeric severity plus hand/prompt fields pass those pre-publication assertions. Earlier GREEN development handoffs are explicitly superseded and source-stale; do not consume them.

No rate-limit/network/dependency blocker remained. No Dart/collector/model/training/math/XP/layout source changes, no device/ADB/default stores/download/install/commit/reset/clean/worktree action. The reusable consumer-shape lesson was added to the existing study-readiness skill.

### Remaining boundaries

Direct AttemptBoundary start/replacement is explicitly declared; the actual production MethodChannel callable handles the other controls. Handler/EventSink delivery is real host wiring but transport is captured/future-mocked, not installed E2E. Synthetic terminal data and native accounting are not recognition or physical measurement. Existing A2b C1 messenger/registry limits remain. Parent must independently run/review this frozen package before A3b Dart/Python consumers; no tasks01/03/05 whole-completion or participant-study gate claim.
- `parent-explicit-1`: exit 0; log `parent-explicit-1.log`; exact command in ledger.
- `parent-full-1`: exit 0; log `parent-full-1.log`; exact command in ledger.
