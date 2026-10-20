# Independent QA — A3a native host producer review 1

## Two verdicts

- **Specification compliance: APPROVE, bounded A3a host-only acceptance.** The frozen authorized extraction and the independently executed parent fixture satisfy the native producer requirements. A3b may consume the exact parent manifest identified below, subject to the acceptance limits in this report. This is not acceptance of A3b or of tasks 01/03/05 as a whole.
- **Code quality: APPROVE WITH MINOR CONCERN.** No Critical/Important blocking defect found in the authorized delta. One Low documentation discrepancy remains. Publication and fixture hardening limits below are explicit limits, not claims of exercised fault coverage.

Review performed against `a3a/task-brief.md`, recovery report/interface/delta/postimages, accepted A2b boundaries, discovery sections 1/5, actual current source, parent logs/XML/ledger and actual parent-produced bytes. Loaded study-readiness and review guidance. This reviewer made read-only Python digest/schema/identity/observation checks; did not rerun Gradle, build, install, use ADB/devices/default stores or execute Dart/Python consumers. Only this report is written.

## Exact reviewed input and execution provenance

Authoritative consumer input for this review:

`benchmarking/study_evidence/20261015/a3a/handoff-parent-1/323291af-c067-46dc-bae1-067d62fab10b/manifest.json`

- Manifest SHA256: `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`.
- Run UUID: `323291af-c067-46dc-bae1-067d62fab10b`; exact integer TEST schema 1; synthetic origin true; producer outcome success.
- Independently read/hash-checked all 11 unique regular, non-symlink artifact files, recorded sizes, and all 42 source digests against current repository files. The 42-source map exactly matches the frozen full snapshot and both parent precompile ledger snapshots. All seven authorized postimages also match `controller/a3a-parent-verification-1.json` and `a3a/recovery-final-source-postimages.json`.
- Independently parsed preserved `parent-explicit-1-xml`: 5 tests, zero failures/errors/skips; its producer stdout names this exact manifest. Parsed `parent-full-1-xml`: 17 suites, 170 tests, zero failures/errors/skips. Both logs show BUILD SUCCESSFUL; full log has executed `:app:testDebugUnitTest` and `:app:compileDebugAndroidTestKotlin` task lines without UP-TO-DATE. Source compilation is not instrumentation execution.
- Parent records the 82 protected originals and eight accepted A2a files unchanged, with accepted A2b MainActivity/factory preimages verified. Those wider preservation assertions are credited to the parent verification, not represented as a fresh independent 82-file audit by this reviewer. MainActivity/factory are intentionally changed, not falsely described as unchanged A2b source.

Worker `handoff-final3-20261016/22ebc4d3-32ee-4bf1-bb54-3708ede613d2` is retained same-source worker evidence, not the selected parent consumer input. Older development outputs remain superseded.

## Specification and implementation findings

Paths below abbreviate `K = app/android/app/src/main/kotlin/com/kumpas/kumpas_app/` and `T = app/android/app/src/test/kotlin/com/kumpas/kumpas_app/`.

### Actual control reuse and export ownership — satisfied

`K/MainActivity.kt:57–59,64–146` registers the same owner-bound callable invoked by host tests. The extraction retains the reentrant pipeline lock, current-owner rejection, permission check, dispatch cases and fixed error mapping. It does not duplicate a test switch. `:174–178` binds export acquisition to the initialization factory before publication. `K/ActivityResourceFactory.kt:9–10,27` fails closed for non-opted-in injected factories, while production receives applicationContext at MainActivity `:48` and creates its fresh helper normally. MainActivity `:114–120` closes that helper in finally on export success/failure. Focused tests `T/HostStudyFlowTest.kt:26–68,115–120` cover actual export acquisition, captured raw-handle closure, omitted acquisition and stale control owner.

No new ownership/synchronization regression is apparent in the frozen production delta. Existing A2b subscriber/resource contracts are preserved; their accepted tests remain in the parent full suite. This proves callable reuse by source and host execution, not real BinaryMessenger registration.

### Real isolation and native flow — satisfied within declared seams

`T/HostStudyFixture.kt:17–62` provides fresh scratch roots, distinct database/internal/external/preferences storage, canonical containment, both database-open overloads, self-returning applicationContext and explicit file-backed Android SharedPreferences with unique namespace. Database helpers/raw handles are tracked (`:63–86`), and cleanup attempts later owners/handles/preferences/root despite earlier failures (`:96–110`). The isolated paths actually used by SessionManager/DataExporter/BenchmarkMode do not fall back to application participant stores. Safe resource handles/assets replace detectors/interpreter; no inference occurs.

`T/HostStudyProducer.kt:77–146` executes initialization, native session/identity/assessment/history controls, synthetic terminal acceptance, independent SQL queries and real Handler/EventSink drain. Primary persisted row/result count is exactly one, duplicates do not add rows/delivery, and cancelled stale input remains absent. ACK calls execute the real callable. Attempt start/replacement is explicitly direct production AttemptBoundary setup because the bare Activity has no permission context; it is not an executed camera-permission/startAttempt path.

Actual artifact inspection confirms 25 controls, including one each of CONTROL_FAILED assessment insert, EXPORT_FAILED writer acquisition and CLEAR_FAILED managed-directory purge. No success response is substituted for these errors. The pre/post assessments and failed insert are checked against real SQLite (`:99–106`), not a copied persistence implementation.

### Export, failure, purge and reopen — satisfied

`T/HostStudyProducer.kt:147–180` adds a foreign participant with real attempt/assessment data and retains exact external/internal export bytes. Reviewer independently recomputed each export's scoped summary from the envelope's independently queried SQL rows: one session, one attempt, two assessments for the selected participant. The foreign records are not exported. Failed export preserves prior completed bytes and closes its temporary helper.

The queued terminal/replacement sequence (`:182–195`) preserves committed persistence while suppressing stale posted UI; stale identity-scoped cancellation leaves replacement deliverable. Snapshot totals at that stage include three attempts across two participants, not three primary results. Partial purge (`:196–209`) truthfully retains SQL rows after some files were removed, then removes only the synthetic blocker and retries actual clear. Clear/reopen (`:210–241`) shows one replacement participant, empty sessions/attempts/assessments, purged exports/legacy residue and surviving unrelated sentinels. Identity remains stable across owner/helper closure and a new preferences instance. Reviewer independently checked actual clear/reopen rows, identity relation and empty export payload.

### Handoff typing and benchmark bytes — satisfied for this artifact

Reviewer compared `app/lib/feedback_engine/models.dart:27–32,56–68` to actual event/history JSON using strict Python JSON type assertions corresponding to the Dart casts. All required fields match, including numeric severity and string hand/prompt. Exact delivered event text equals `attempt-event.json`, the primary envelope string and captured delivered-events entry. This is a shape/byte check, not execution of Dart deserialization/UI. The earlier feedback-schema RED remains documented; no claim that native persistence itself validates the Dart schema.

`T/HostStudyProducer.kt:248–307` executes real BenchmarkMode publication for confirmed/unconfirmed/faulted modes, reads immutable files directly, and verifies unchanged bytes after replacement/stale confirmation. Modes have distinct actual run UUIDs; report schema is integer 2, companion schema integer 1. Actual reports are complete with 1,800 synthetic analyzer accounting calls each. Confirmed/unconfirmed companions have matching run identity and status. Faulted mode has an observed nonempty companion directory and no fabricated companion artifact. Reviewer verified index/scenario identity agreement and all retained hashes. Setup booleans, synthetic APK/revision/camera and accelerated clock are constructed fixtures, not independently attested hardware metadata.

### Successful publication and negative coverage — satisfied with limits

`T/HostStudyProducer.kt:58–69,243–245,304–307` publishes only after study/benchmark assertions and fixture use-block cleanup return successfully. `T/HostArtifactRun.kt:27–36,50–79` rejects existing/unnormalized/symlink destination paths, invalid artifact basenames/kinds/identities and duplicates; requires exact output set, stable source snapshot and matching regular-file bytes before success publication. `T/HostStudyFlowTest.kt:76–111` executes existing/escaping/symlink/duplicate/missing/tampered/stale negatives plus post-publication rejection. Producer assertion failures are logged and rethrown, not converted to success.

Limits: source hashes are runtime snapshots, not compiler attestations; actual parent precompile equality and source stability supply the missing binding here. The publisher is not a hostile concurrent-filesystem security boundary or power-loss-durable transaction. It writes manifest directly with CREATE_NEW then reads back (`HostArtifactRun.kt:75–83`); no injected manifest-write/readback fault matrix or rollback guarantee is established. Therefore standalone discovery of a success manifest is insufficient: consumers must require its matching successful producer-suite evidence. This does not invalidate the observed successful parent run.

## Nonblocking finding

**L1 — Low: handoff documentation still selects worker output.** `a3a/handoff-interface-v1.md:3–14` calls worker final3 the current and only explicit handoff; `a3a/recovery-report.md:27–28` similarly calls it the sole final candidate. That contradicts the parent-selected run for this review and could steer A3b toward the wrong execution identity despite matching source. No source repair or artifact regeneration is needed. Parent acceptance/A3b brief must explicitly supersede that selection with the parent manifest and digest above (a separate binding record is sufficient; do not rewrite retained execution evidence). This report makes that discrepancy explicit rather than treating the worker path as parent output.

## Exact acceptance limits for A3b

1. Pin the parent run and manifest digest above, successful matching parent producer XML/ledger, integer TEST schema 1, source snapshot and all 11 artifact digests/sizes. Never select a directory by “latest,” silently substitute worker/historical outputs, or reconstruct report/control/event bytes. Preserve originals; place consumer-negative mutations in separate synthetic fixtures.
2. A3b must implement and execute its own fail-closed missing/stale/duplicate/tampered/identity/type checks and real Dart/collector reader-to-isolated-sink assertions. None are accepted by this A3a review. Faulted companion remains genuinely absent, not a manufactured JSON failure payload.
3. Real evidence here is host MainActivity control/event logic, posted Handler capture and isolated SQLite/preferences/export/purge/reopen. Transport to future Dart/Python processes is mocked and layered. No continuous installed CameraX→BinaryMessenger→Flutter→persistence integration, camera/recognition, detector/interpreter release, physical FPS/latency/thermal, expert/model/human outcomes or participant-study authorization is established.
4. Preserve A2b C1: differing-messenger handler detachment and same-registry-ID retry are not guaranteed by these callable tests. Do not infer configureFlutterEngine startup/removal from the source reuse.
5. Error evidence is bounded to the actual injected assessment insert, export-open and partial filesystem purge failures plus linked prior regressions. This is not every SQLite/preferences/close/publication fault at every integration stage. Synthetic qualification fields cannot close physical gates. No whole-task or broader phase closure follows from these two approvals.

## Result

A3a is acceptable as a frozen, executed native host artifact producer with the explicit parent-input binding and retained Low concern above. No implementation changes requested before bounded A3b consumer work; broader integration, physical and study gates remain open.
