# Follow-ups independent specification and quality review

## Verdicts

- **Specification: PASS**, limited to B1-R1 numeric rejection and C1-Q1/C2-L1 persistent coverage.
- **Code quality: PASS.** No new blocking or nonblocking defect found in the reviewed four-file scope. All three original LOW findings are closed within that scope.
- **Parent acceptance remains required.** This is not whole-application, Android parity, physical performance, model quality, full-source provenance, human-study or participant-collection acceptance.

The report began incrementally before verification. Loaded study-readiness and verification skills. Read PRD, phase gates, approved host-completion design and plan, all three complete original reviews, follow-ups report/ledger, full four-file postimages, before/after snapshots, exact delta and parent evidence. Inspected unchanged inspector/export-CLI production seams and the original B1 verifier without running that verifier.

Review was read-only inside the repository except this report. No source edits, devices/default stores, installations, builds, cloud-source reads, training, real classifier inference/conversion, commits/reset/stash/worktrees or historical-output rewriting occurred. Synthetic tests used fresh scratch roots; compatible Holistic execution was synthetic only.

## Frozen identity

Each current hash independently matches `controller/followups-parent-verification-1.json`, the complete additive postimage reconstructed from `controller/followups-review-package-1.diff`, and `followups/after/`. Preimages match `followups/before.json`. `followups/source.diff` exactly equals a fresh unified diff of saved before/after snapshots. Four current hashes were rechecked after execution.

| File | SHA-256 |
|---|---|
| `benchmarking/pipeline_parity.py` | `d9d1e4ba4a938b080cd408936f978a166dc19bf7eab1ee4a56c18e875a6342b4` |
| `benchmarking/test_pipeline_parity.py` | `73d9c465ade5ca177619371a8cc6b62a9639e34ffee63faca30aa1d20ce24c25` |
| `benchmarking/test_inspect_release.py` | `75ae48ac36ccc1a753260aafd660998ea5b5fab53f8512cc16d046fd448d1498` |
| `evaluation/test_export_cli.py` | `66640847482f3421ffdc90e2912e7bdcd0963127a14bc66c8aba7dae0eb3fa43` |

C1 production `inspect_release.py` remains `ecf9f2f33f2fc1f28bf9d6efc47a2f6f661e1e9fef929180cafe920c42eb5bb3`; C2 production `export_cli.py` remains `2975b0e7a0f2dd13f720166fdc85fbd4f7ea538b599d11c60f42c1bd453b18c7`. Every historical C1/C2 parent source role independently matches either the saved before snapshot of its changed test or current unchanged bytes. No historical source binding was updated.

## Fresh independent execution

All commands ran from the exact repository with explicit `TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`, existing environments and `-B -E`.

1. `training/.venv/bin/python -B -E -m unittest benchmarking.test_pipeline_parity -v`: **17 passed, zero failures/errors/skips, exit 0**, 2.183 seconds. Includes actual Holistic processing of a new synthetic black frame, not historical real fixture regeneration.
2. `/opt/homebrew/bin/python3.11 -B -E -m unittest benchmarking.test_inspect_release evaluation.test_export_cli evaluation.test_legacy_export evaluation.test_synthetic_descriptive -v`: **49 passed, zero failures/errors/skips, exit 0**, 3.467 seconds: 31 inspector and 18 evaluation methods.
3. Three reviewer-only methods, executed in memory under general Python: **3 passed, zero failures/errors/skips, exit 0**, 0.482 seconds:
   - Injected a nonfinite comparator return into an in-memory executable-module copy. Strict serialization returned exit 1 and exactly `{"ok": false, "error": "comparison_failed"}` without invoking patched `Path.write_text`; existing output sentinel remained intact. This independently reaches serialization's defense, not merely the arithmetic guard.
   - Verified NumPy caller error policy restoration after all three arithmetic rejections. Executed the historical comparator snapshot in memory and reproduced its nonfinite report for finite opposite-sign extremes; strict JSON rejects it. No checkout rollback was needed.
   - Ran six actual CLI success controls: identical `1e308`, single-frame `1e306` versus zero, and four-frame `1e100` versus zero, in both bound and explicit legacy modes. Stdout/file reports agree, stderr is empty, labels remain correct, constants are strict JSON and maxima are not clamped.
4. Scoped `git diff --check`: exit 0. Final source hashes and preservation inventory still match after reviewer execution.

**Distinct fresh coverage: 66 canonical methods plus 3 reviewer-only methods; all 69 passed in their explicit final runs.** Subtests and repeated runs are not additional methods. An initial extra-probe invocation used unrestricted `unittest.main`, which also rediscovered imported parity tests: 20 run, 19 passed, 1 explicit general-environment MediaPipe capability skip. It was corrected to select only the three extra methods. That redundant run is disclosed, not added to totals; compatible execution independently passed the detector method. Native MediaPipe startup warnings appeared during the synthetic compatible test, not the tested compare subprocesses.

Separately checked parent log digests against parent JSON and parsed **17 parity, 31 inspector, 18 evaluation**, all OK without skips. Worker execution is separately dated **October 18, 2026** in `command-ledger.jsonl`: inspected `final-benchmark.log` (**124 run, 122 passed, 2 capability skips**) and `final-compatible-parity.log` (**21 passed, zero skips**, synthetic campaign included). Reviewer did not freshly rerun broad discovery or the 21-method campaign. These overlapping saved executions are not summed with reviewer totals.

## Finding closures / specification and quality

### B1-R1 — original LOW arithmetic robustness defect: CLOSED

**Locations:** `pipeline_parity.py:223–236,325–340`; persistent tests `test_pipeline_parity.py:21–97`.

Local `np.errstate(over="raise", invalid="raise")` encloses subtraction and block mean/max computation. Floating-point failure becomes fixed `ValueError("nonfinite comparison arithmetic")`; explicit finiteness checks additionally guard error arrays and returned reductions. No normalization, dimensions, feature-range policy or clamping changed. Rejection preserves the existing reduction algorithm; it does not introduce a numerically rescaled mean to accept an overflowing reduction.

Persistent library and real CLI regressions cover three classes: `1e308 - (-1e308)` subtraction, one-frame `1e308` mean reduction, and four-frame `1e306` aggregate reduction. Both strict bound and explicit legacy modes reject. Library rejection has no warnings. Each CLI fault runs against absent and existing sentinel output: nonzero exit, fixed safe JSON, empty stderr, no Infinity token, no creation/truncation. Ordinary and representable large-finite controls pass.

Library legacy default and strict `require_clip_binding=True`, CLI binding-required default and `--legacy-frame-only` semantics are preserved. Native replay schema compatibility and explicit non-evaluation of class predictions remain unchanged. Successful compare JSON uses `allow_nan=False` before `args.output.write_text(serialized)`; failure JSON is strict too. This fixes numerical-report rejection, **not atomic parity-output I/O**: later partial I/O on an otherwise valid report can still affect a target. No hostile-filesystem or power-loss guarantee is inferred.

Read the complete saved RED failures: 3 methods ran, ordinary/large-finite control passed, 12 failed subtests because library ValueError was not raised and actual CLI overflow exited zero. Subsequent saved GREEN, fresh canonical execution and independent old-snapshot reproduction support genuine defect closure; no fake RED was introduced.

### C1-Q1 — original LOW persistent-test gap: CLOSED, coverage-only GREEN

**Locations:** `test_inspect_release.py:285–355`; unchanged production `inspect_release.py:133–177`.

Three maintained methods now exercise the exact prior gap:

- Second fsync after publication/readback/stage removal: verifies final bytes exist at fault time, exactly two fsync calls, then owned final cleanup.
- One-byte partial write followed by exception: verifies one byte was written and owned stage/final cleanup.
- Final-target open failure after link: verifies final bytes exist and the intended basename fault occurs exactly once, then owned publication cleanup.

Every case preserves pre-existing stage and completed-output sentinels. Fresh 31-method execution passes. Saved first-run GREEN agrees with the original reviewer observation that production already behaved correctly. No C1 production repair or fabricated RED is claimed.

### C2-L1 — original LOW persistent ownership/snapshot gap: CLOSED, coverage-only GREEN

**Locations:** `evaluation/test_export_cli.py:115–166`; unchanged production `export_cli.py:58–89,105–119`.

Two maintained methods preserve the exact requested behavior. Input pathname replacement occurs only after snapshot/validation. Successful report content derives from original bytes; manifest input digest matches those original bytes rather than the invalid replacement, and report digest matches publication.

The cleanup case finishes owned manifest acquisition/readback, checks owned device/inode identity, renames and retains that inode, creates a different-inode unowned sentinel at the canonical path, then raises. CLI returns 2 with fixed `OUTPUT_READBACK`; unowned sentinel survives and displaced original inode/report linkage remain verifiable. Keeping the displaced inode alive prevents reuse-based nondeterminism. Both methods pass against unchanged production alongside all other evaluation tests. Initial GREEN is coverage evidence, not a repaired production defect or manufactured RED.

## Preservation / historical provenance

Independent hashing used regular-file and macOS DATALESS checks before open, plus descriptor flag checks. No historical NPZ/video source path was opened; expected hashes came from named historical records, not values learned from current targets.

- **82 protected originals, 42 native producer sources and 4 A3b consumers match.** Protected expectations equal `controller/host-baseline.json`; native expectations equal the accepted manifest after checking its binding digest; A3b equals its accepted source map.
- Before inventory contains **2,730 entries / 1,598 distinct paths**. Excluding only seven relative/absolute aliases of the four authorized files, **all 2,723 other entries match**, including final post-execution verification. The newly created reviewer report was not a pre-existing inventory exception.
- B1 completion manifest remains `1cca1526355e9d4ce6c41102a0a6fa474a15dd77bbac2b09daee1ec85e70c452`; selection remains `bc7bb2bd85359cc7242ecfb4bba84e267303c911061a0c1a8fa8ce9c980bf8ad`. Verified **6 fixture manifests/references, 180 PNG digests**, listed outputs, replay/reference frame-hash agreement and binding equality, without source reads/regeneration.
- Every historical B1 generation source role was compared. Exactly one current-source drift exists: comparator old `cc905b5494e1fe78d7c4d3de3bcf05772499946538d42f404f17acad3c43d93d` versus current `d9d1e4ba4a938b080cd408936f978a166dc19bf7eab1ee4a56c18e875a6342b4`. Historical bytes remain in `followups/before/benchmarking/pipeline_parity.py`; other declared generation roles match. Old fixtures do not acquire new-source provenance.
- `b1/verify_evidence.py:56` would reject that intentional comparator binding drift if reached. It first reads original video/NPZ sources, so it was **not run**. Safe artifact readback is not renewed full-source verification; no manifest was rebound to conceal drift.
- Accepted B2 current sources and **6 historical output digests plus campaign/incomplete-manifest digests** match named B2 records. **3 historical APK hashes** match `20261007/controller/owner-parent-verification-1.json`. These establish retained bytes, not fresh build/inference/conversion, installed behavior or strict ABI acceptance.

## Issues and remaining limits

No source defect or blocking review issue found. The redundant reviewer discovery/skip is disclosed above. Worker discovery failure with `-t .` and early DATALESS-environment capture refusal remain preserved historical issues, not hidden successes. Final report replacement initially met a tool stale-write guard; reading the current incremental report resolved it without source changes.

Only this assigned report was created/modified inside the repository by QA; synthetic roots were temporary and extra probes ran in memory. Parent should rematch the four postimages and record acceptance of these three narrow closures. Continuous installed integration, physical phone/performance, live signer, linguistic/anatomical, model/full-source, human instrument/inferential and participant-authorization gates remain unchanged.
