# C1 independent spec and quality review

## Verdicts

- **Specification: PASS for bounded C1 inspector tooling and historical packaging-consistency inspection.** The new source implements the approved explicit-file, independently bound, fail-closed host contract. This does not accept a fresh build or strict ARM64-only packaging.
- **Code quality: PASS, with one low-priority persistent-test coverage follow-up below.** No blocking implementation defect was found in either complete source postimage or the independently exercised paths.
- **Parent acceptance remains required.** This report is independent QA evidence, not a package/final-study acceptance record.

## Scope and requirement basis

Read both full source files, C1 task brief/report/verification summary, current parent verification, full approved host-completion design/plan, PRD, phase gates and tooling discovery. Checked the full additive postimages in `controller/c1-review-package-1.diff` against the current files; both match byte-for-byte. Package C's artifact tooling is reviewed here; research utilities and parent-owned final fresh builds are not included. Loaded `kumpas-study-readiness` and `verification-before-completion`.

Review was read-only except this assigned report. Synthetic tests used existing `/opt/homebrew/bin/python3.11 -B -E` and `TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`. No source changes, install, build, device/ADB, default-store operation, inference/training, commit, reset, stash, worktree or cloud hydration was performed.

## Frozen source identity

| File | SHA-256 |
|---|---|
| `benchmarking/inspect_release.py` | `ecf9f2f33f2fc1f28bf9d6efc47a2f6f661e1e9fef929180cafe920c42eb5bb3` |
| `benchmarking/test_inspect_release.py` | `03450c2a0035116910d78d514a9d90e446f0679c8eb1626ea0870090ee98eae9` |

Hashes were independently calculated and rechecked after execution. They match `controller/c1-parent-verification-1.json` and the reviewed diff postimages.

## Independent execution

1. From the repository, executed:
   `TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /opt/homebrew/bin/python3.11 -B -E -m unittest benchmarking.test_inspect_release -v`
   **28 tests run, 28 passed, 0 failures/errors/skips; exit 0**, 3.033 seconds.
2. Executed an additional **10 reviewer-only in-memory unittest methods**, using the production inspector and existing isolated synthetic fixture setup. **10 passed, 0 failures/errors/skips; exit 0**, 1.380 seconds. These covered extra exact-type rejections; native/asset case aliases and file-parent collisions; CRC-corrupted payload rejection with a rebound expected APK digest; protected-parent symlink rejection; failure on the second (directory) fsync after publication; partial-write cleanup; final-target open failure cleanup; in-place APK mutation; protected-source mutation after archive inspection; and nonfinite/private unknown-key JSON with fixed error output. Subtests are not counted as separate methods. These probes were executed via tool Python command strings and were not added to repository source.
3. Independently reran the actual historical public CLI in stdout-only mode against `app/build/app/outputs/flutter-apk/app-release.apk`, using `c1/historical-release-packaging-expectation.json`. **Exit 0, empty stderr, exact-byte match** to `c1/historical-release-current-source-result.json`; output SHA-256 `ea6af87cb75419d631e099955aa74dcb18c3e12e1606f3f7b7858e5ebe149a83`.
4. Reran the same actual CLI with `c1/historical-release-arm64-expectation.json`. **Exit 1**, empty stderr, exactly `{"ok": false, "error": "verification_failed"}`. No output target was supplied or created. Strict ARM64 rejection is correct, not a failed strict-acceptance claim.
5. Independently hashed all **1193** entries in `c1/preservation-before.json`: **0 mismatches, 0 unread/DATALESS entries**. Independently checked all **82** original protected entries against `controller/host-baseline.json`: **0 mismatches**. The packaging expectation's protected map equals those baseline expected values, including independent asset bindings. Accepted B1/B2/native/source-bound fixtures covered by these maps were unchanged.

Fresh reviewer execution totals are **38 test methods passed, zero skips**, plus the two actual historical CLI invocations. Broad discovery was not independently rerun by this reviewer. Separately inspected saved `current-source-broad.log`: 118 run, OK with 2 skips (116 passed); those explicit MediaPipe capability skips are not passes. Inspected saved parent-focused log: 28 run, OK. Do not add these saved counts to fresh reviewer execution.

## Specification and implementation checks

- `inspect_release.py:60–89,249–250`: exact manifest keys and built-in integer schema typing, supported artifact label/ABI vocabulary, unique native names, strict lowercase SHA-256 syntax, all five fixed asset paths, asset-source identity and independent protected-map equality. Duplicate JSON keys and nonfinite constants fail safely. An issuer can deliberately choose a different policy; this is an explicitly trusted expectation, not self-attestation.
- `:180–198,201–233`: protected-byte checks before and after inspection; one open APK descriptor used for initial hash, ZIP reads and final rehash; exact native file/ABI set; every ZIP entry checked for ambiguity, duplication, invalid file types and file/directory collision; archive integrity checked before required asset/native hashing. Real Android resource case differences remain distinct, while asset/native case aliases fail. Native hashes and namespace membership are reported without pretending to validate ELF architecture.
- `:104–177,255–258`: contained explicit output target under an existing directory; no-follow parent walks; exclusive stage creation and hard-link publication; staged and final exact-byte readback; failure cleanup that preserves existing outputs. Existing regression tests plus reviewer post-link fsync/open/partial-write faults pass. These are bounded trusted-filesystem guarantees, not power-loss or malicious concurrent-filesystem guarantees.
- `:236–263`: malformed argument/JSON/ZIP/I/O failures become one fixed JSON error with nonzero exit, not private path, exception or payload echoes. Successful output includes exact expectation and current inspector hashes, while explicitly keeping source-build provenance, signature verification and runtime verification false.

## Historical artifact adjudication

Independently located the expected APK digest in the named prior owner record, not merely in C1's result: `benchmarking/study_evidence/20261007/controller/owner-parent-verification-1.json`, `artifacts.release_arm64`, path `app/build/app/outputs/flutter-apk/app-release.apk`, 66969546 bytes, SHA-256 `da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266`. The fresh historical CLI verifies these same bytes.

The accepted *bounded observation* is complete native namespaces `arm64-v8a`, `armeabi-v7a`, `x86_64`, with Flutter library pairs only under `arm64-v8a`. The explicit three-ABI/native-name policy was frozen **after observation**; it is current consistency capture, not preregistration. C1 report lines 111–128 state that limitation correctly. The strict one-ABI policy rejects the artifact. Mixed native names alone do not prove a deployment defect, and this review neither changes build configuration nor instructs an ABI repair.

Current checkout asset/protected hashes are inspection-time expectations, not historical build-source provenance. The inspector's `fresh_build` label cannot supply that provenance. Fresh-build execution/identity and intended ABI acceptance remain parent-owned. ZIP names and hashes do not establish ELF correctness, signature, Android-manifest policy, runtime behavior, physical performance, expert validation, study readiness or participant authorization.

## Concrete quality finding

### Q1 — LOW, nonblocking: retain the later publication-fault regressions

**Locations:** `benchmarking/test_inspect_release.py:261–283`; production boundary `benchmarking/inspect_release.py:151–177`.

The committed test patches `fsync` to fail on its first call and also covers link/readback corruption; it does not persist regressions for failure on the *second* fsync after the final link, a partial write, or final-target open failure. This is a coverage gap, **not a reproduced implementation failure**. The reviewer executed all three fault cases; each raised as expected, removed its owned target/stage, and left no success artifact.

**Reproduction for the coverage observation:** run the focused suite above and inspect the fault injection at test lines 264–268: unconditional `side_effect=OSError(...)` reaches only the first fsync. To exercise the distinct later path, wrap the real `os.fsync`, count calls, raise on call 2, invoke `publish` in the isolated `ReleaseTests` fixture, then assert the call count is 2, the target is absent and `.inspect-*` is empty. This exact reviewer probe passed. Equivalent executed probes wrapped `os.fdopen` to write one byte then raise, and patched `os.open` only for the final basename; both cleanup assertions passed.

**Suggested follow-up:** preserve these synthetic cases in the maintained suite in a separately authorized source edit. No fix or regression addition was performed during this read-only review. Parent may accept the bounded source with this low-priority follow-up explicitly recorded.

## Review execution issue

The first combined read-only verification command completed source hashes, preservation/protected checks and both real CLI invocations, then exited 1 because the reviewer's diff parser incorrectly treated an absolute-style diff header as repository-relative. This was a reviewer harness error, not an inspector failure. A corrected scoped suffix parser reran successfully and confirmed both full postimages exactly. No source/evidence was modified to recover.

## Remaining acceptance boundary

Only this report was created/modified by QA. All assigned source and historical evidence remains unchanged. Parent must adjudicate the low-priority coverage follow-up, rematch the source hashes, and own final acceptance/fresh-build disposition. Installed integration, target-phone/physical measurements, model/expert/human gates and participant authorization remain open.

