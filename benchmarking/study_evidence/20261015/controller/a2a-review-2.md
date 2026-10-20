# A2a independent QA re-review — repaired lifecycle/cache handoff

## Verdicts

- **Specification: APPROVE for the bounded A2a host lifecycle/cache requirements and R1 repair.** The finite delayed-success and finite end-error handoff is repaired across actual screen-observer lifetimes. Original clear/reply-order fences, pending-start departure handling, native timeout semantics and A1Q1 assertions are preserved. No remaining blocking in-scope finding was identified.
- **Code quality: APPROVE for this scoped package.** The shared observer queue and explicit non-adoptable ending identity address different failure modes without an unscoped compensating end or a broad caller-contract change. Error isolation, current-intent rereading and existing cache fences are coherent. B1 below remains a documented low-severity boundary, not native identity atomicity.
- These are independent review verdicts, **not broader runtime, host-project, installed-integration or study acceptance**. Parent acceptance remains separate.

## Review basis and independent checks

Read both binding briefs, original implementation report, repair report, original independent review, complete eight-file `controller/a2a-review-package-2.diff`, current scoped source/tests, frozen `controller/a2a-parent-verification-2.json`, host design and protected baseline. Inspected actual `PracticeScreen` construction/disposal, session caller search, native session dispatch and timer cancellation/close paths. The HEAD-relative package includes carried native/resource and A1 exporter-test work; it is not all newly attributable to this repair.

Independent checks executed during this review:

- Recomputed all **8 scoped source/test SHA-256 values** against the frozen parent manifest: **8 match**, including after the host tests.
- Reconstructed each tracked package diff against its HEAD source and compared the two full-new-file sections with disk: **all 8 package files match current source**. An initial literal comparison with default-context `git diff` differed because of diff context; reconstruction resolved this without any source change.
- Recomputed all **82 protected files** against baseline `expected` digests: **0 mismatches**.
- `git diff --check`: **exit 0**, before and after focused execution.
- Executed the current focused tests independently: **40 passed, exit 0**. This included the repaired finite handoff/error scenarios, B1 characterization and preserved repository/clear tests. No production/test source was edited or reverted, and no independent RED rerun is claimed.

Exact fresh command, working directory `app/`:

```text
/opt/homebrew/bin/flutter test --no-pub test/session_clear_test.dart test/session_lifecycle_race_test.dart test/session_repository_race_test.dart --reporter expanded
```

Execution used the existing `~/.hermes/cache/scratch/kumpas-a2a` TMPDIR and exclusive existing `~/.hermes/cache/scratch/kumpas-gradle.lock`; output returned directly through the review tool. Terminal result: `00:00 +40: All tests passed!`. The implementation runner was not invoked because it would append other repository evidence files.

Read parent `a2a/parent-fix1-flutter.log` (`+75: All tests passed!`) and `parent-fix1-analyze.log` (`No issues found!`), consistent with the frozen parent record. These **75 full Flutter tests and clean analysis are parent executions, not fresh full-suite executions by this reviewer**. Parsed preserved `a2a/final-jvm-xml/` results: **42 SessionManager + 22 DataExporter**, zero failures/errors/skips. Native source/tests match the frozen snapshot and were not rerun for the Dart repair or this review; these **64 targeted prior JVM tests are not a fresh or full native suite**.

Package SHA-256: `840de48520c1edc524a72d16d0efd843f4f2ddc6c903b7087972132e1e138816`.

## Findings and repair assessment

### R1 — Medium / previously blocking: RESOLVED within the finite-reply observer boundary

Locations: `app/lib/session/session_repository.dart:23–35,43–46,72–81`; `app/lib/session/session_lifecycle.dart:46–99`.

The original failure was reachable without an arbitrary external caller: old screen dispose dispatched end, replacement adopted its cached ending ID, then successful old end reply left the replacement sessionless. `PracticeScreen:53–58,303–312` still constructs a distinct observer per screen and does not await departure. The repair correctly puts coordination in the shared repository, not only inside one observer.

Every observer reconciliation turn now waits behind the previous observer's pending operation. When an old end succeeds, the replacement sees cleared cache and starts a fresh session. When end errors before **or** after its native effect, the queue releases, while `_endingSessionId` keeps the uncertain cached identity unavailable for adoption. Replacement start then closes any surviving native old session using the normal start contract. A later obsolete-owner event cannot end the committed replacement because ownership/cache identity no longer matches. The old owner retains its identity if end throws, preserving same-observer retry.

The new tests at `session_lifecycle_race_test.dart:34–204` model native effects at dispatch separately from replies, and cover finite success, error on both sides of the effect, replacement departure/reentry, and successful/partial-failed clear during handoff. They capture the replacement resume future and release the withheld old reply before awaiting it. This changes synchronization from the old reviewer probe without changing the causal ordering; it avoids deadlocking a correct shared queue. Preserved RED logs show the original missing replacement start and both error-position failures. Fresh focused execution passes the repaired cases. This conclusion is based on the mechanism and schedules, not merely on the full-suite green count.

### B1 — Low / non-blocking boundary: STILL PRESENT and honestly characterized

Locations: `session_lifecycle.dart:93–99`; `session_repository.dart:25–27,60–81`; native `MainActivity.kt:86–91`.

Only observer operations join the shared queue. An arbitrary direct repository start can take effect while its reply is withheld, leaving the old ID cached; an old observer's cache-equality check can then permit native unscoped end to close that replacement. `session_lifecycle_race_test.dart:206–234` deliberately preserves this characterization and passes. **Cache identity comparison is not native identity-scoped end or distributed atomicity.**

The current production Dart call search still finds session start/end consumers only in `SessionLifecycleObserver`; no independent direct start/sync consumer was found. Accordingly B1 is not promoted to a second reachable production blocker and does not require expanding this bounded fix's caller contract. Future consumers must not assume arbitrary overlapping direct calls are coordinated.

## Original bounded requirements retained

| Requirement | Assessment and evidence |
| --- | --- |
| Repeated native pause, resume/replacement and close; original 60-second deadline | Supported by unchanged `SessionManager.kt:124–147,240–249` and deterministic Looper tests. Duplicate pause retains the first runnable/deadline; cancellation reaches that runnable. Existing tests assert 59,999/60,000ms, foreground/replacement preservation and captured callback removal after close. Prior targeted JVM execution only; no fresh native run. |
| Late participant/start/sync after clear entry or completion | Current epoch checks fence cache commitments, with invalidation on entry and in finally. Repository tests cover each method before/during clear for success/partial failure. This is cache fencing, not an atomic purge/read transaction; a during-clear completion can transiently cache before finally, and old callers still receive their original payloads. |
| Partial clear failure/revision/post-clear usability | Finally invalidates participant, active and ending identities and increments revision once; the original native error propagates. Focused tests verify fresh identity/session calls remain usable. No rollback fabricated. |
| Out-of-order start/end/sync replies | Latest-issued session command plus clear epoch gates cache/marker commits. Tests separate native effects from reply delivery and preserve a later replacement against old replies. They do not cancel native effects or turn an old response payload into current ownership. |
| Duplicate entry/resume; departure during pending start; inactive | Per-observer intent/departure tracking remains intact inside the shared coordinator. Tests cover leave/paused/hidden/detached, immediate cached departure, inactive as transitional and reentry; obsolete continuation cannot end a cache-visible committed replacement. Cross-screen R1 now has explicit coverage rather than substituting a same-observer test. |
| Fire-and-forget errors and deterministic retry | `_drain` catches failures with fixed diagnostic text, clears pending work, and retries on a later event. The repository's recovered tail prevents one failed observer poisoning another. Finite end-error handoff no longer requires an event on a disposed old screen to make a new observer usable. No automatic retry/backoff claim. |
| A1Q1 original borrowed SQLite handle | `DataExporterTest.kt:348–367,395–407` captures the original handle before covered failed exports and checks it before a getter could reopen it. Still resolved, coverage-only GREEN; no exporter production change in this slice. |

## Explicit limits and carried observations

- **No new deadlines were implemented.** A permanently lost reply can hold the shared observer queue and block later observers too. Finite replies/errors above do not prove permanent-loss recovery; that exclusion is not being used to conceal a finite R1 failure.
- Fresh observers still initialize foreground false, and `PracticeScreen.initState` does not seed the binding's already-current lifecycle state. Ordinary route entry without a delivered resume is not established to start a session. This was explicitly carried/excluded in the first review; this repair neither fixes nor newly introduces it, and R1 regressions explicitly deliver resume.
- Concurrent clears, arbitrary transport command reordering, native timer persistence failure, process death, multiple simultaneously active screen owners and automatic recovery with no later event are not newly established contracts.
- Native commands execute before `result.success` in inspected dispatch, but mocked effects/replies and separate host suites are not uninterrupted installed Flutter/CameraX/SQLite integration. Native attempt recording can create a session on demand; no stronger Dart ownership guarantee is inferred from that fallback.
- No A2b resource/activity/stream acceptance, phone/camera measurements, physical performance, training/model promotion, research scoring or participant-study authorization follows from these verdicts.

## Reviewer changes and issues

Only `benchmarking/study_evidence/20261015/controller/a2a-review-2.md` was created intentionally inside the repository. No scoped source/test, original review, baseline, frozen manifest or parent log was changed. No scratch probe source was needed. Flutter host tests may update ordinary generated test caches; no app/APK/Gradle build, installation, ADB/emulator, default participant store, training or commit was performed.

One read-only search wrapper initially assumed a `matches` field instead of this tool's `matches_text`; the corrected search completed. Package comparison initially used incompatible diff context, then exact reconstruction verified all eight files. Neither diagnostic changed source, affected execution, or leaves an unresolved verification blocker.
