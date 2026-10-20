# A3a TEST handoff interface — version 1

## Current handoff (explicit, not “latest directory” discovery)

Repository-relative root:
`benchmarking/study_evidence/20261015/a3a/handoff-final3-20261016/22ebc4d3-32ee-4bf1-bb54-3708ede613d2/`

Manifest: `manifest.json` under that root.

Manifest SHA256: `4bfa51cf5e4c67b304ef86c869326d2d0dd633337e6c3af6cb2a8cf128725c69`.

Run UUID: `22ebc4d3-32ee-4bf1-bb54-3708ede613d2`.

Use only this explicit handoff for this frozen source. Earlier `handoff-recovery-*` and `handoff-final-20261016-1023` outputs are retained historical/superseded development evidence, NOT approved consumer inputs. The final source digest differs from them. Parent independent verification and specification/quality review are still required before A3b consumption.

## Manifest

`test_schema_version` is the integer **1**. This TEST envelope is separate from, and does not alter, production benchmark schemas.

- `run_id`: fresh canonical UUID, also the enclosing directory name.
- `synthetic_origin`: boolean true.
- `producer_outcome`: `success`, published only after study assertions, fixture cleanup, benchmark assertions, current source digest checks, and exact output readback succeed. It describes the producer scenarios, not installed or physical acceptance. Require the corresponding producer JVM suite to have passed too.
- `transport`: host native callable/Handler boundary, not an installed BinaryMessenger.
- `source_hashes`: repository-relative SHA256 map covering all native main/test Kotlin inputs and app Gradle configuration (42 inputs in this execution).
- `source_hash_stage`: JVM runtime snapshot; the recovery runner independently hashes before Gradle compilation and verifies unchanged bytes after execution. `explicit-handoff-3` in `recovery-command-ledger.jsonl` has the precompile snapshot; it matches the manifest and current source.
- `artifacts`: unique basename paths, SHA256, byte length, fixed kind, fixed identity. All 11 were independently read back and hashed after execution.
- `scenarios`: passed study scenario UUID/primary result count and three actual native benchmark mode identities.

Consumers must explicitly bind the expected run/manifest, exact integer schema, success plus producer suite outcome, source snapshot and all artifact digests. Reject stale/missing/duplicate/tampered payloads. Exhaustive Dart/Python consumer validation belongs to A3b; no such consumer execution is claimed here.

## Exact artifacts

| File | Meaning |
| --- | --- |
| `study.json` | Versioned synthetic study envelope and independent observations |
| `attempt-event.json` | Exact UTF-8 string delivered by the real posted Handler to the capturing EventSink, not reserialized |
| `external-export.json` | Exact bytes from actual production external export |
| `internal-export.json` | Exact bytes from actual production fallback internal export |
| `reopened-export.json` | Exact empty export after real clear, helper close, fresh preference instance, helper/session reinitialization |
| `benchmark-index.json` | Mode/run identity, exact report/companion filenames, synthetic setup inputs and explicit absent-companion observation |
| `confirmed-report.json` | Exact immutable native report bytes for executed confirmed full synthetic window |
| `confirmed-control.json` | Exact native confirmed companion bytes |
| `unconfirmed-report.json` | Exact immutable native report bytes for executed unconfirmed full synthetic window |
| `unconfirmed-control.json` | Exact native unconfirmed companion bytes |
| `faulted-report.json` | Exact immutable native report bytes when companion confirmation publication was blocked by a nonempty directory |

There is intentionally **no** `faulted-control.json`: the actual native path was a directory, not a companion payload. The index records null, rather than manufacturing bytes. Mode identity is fixed and each real native run UUID is distinct. Each mode executes 60 Robolectric-clock seconds and 1,800 synthetic analyzer accounting calls, with one synthetic trace. No actual camera/analyzer frames or inference were executed. Any native qualification fields are synthetic validator behavior, not hardware attestation or physical gate acceptance.

## Study envelope

- `test_schema_version`, `run_id`, `scenario_id`, `synthetic_origin`, execution/attempt setup/correlation declarations.
- `primary`: synthetic terminal input string, exact delivered output string, actual attempt identity, history response string and independently queried SQLite table rows. One primary result is persisted/delivered; duplicate and invalidated stale terminal inputs do not add rows/events. History has no durable attempt UUID column; correlation uses the declared unique synthetic labels, class/confidence/match and counts.
- `control_calls`: ordered stage/method/argument/response/error-code records. String responses remain actual native strings. The 25 calls include real assessment failure (`CONTROL_FAILED`), export write failure (`EXPORT_FAILED`) and partial purge failure (`CLEAR_FAILED`), each followed by verified observations/retry where appropriate. No successful reply was accepted for a failed operation.
- `export_stage_independent_rows`: includes a foreign participant with a real attempt and assessment; both participant exports contain one primary attempt/two assessments and exclude the foreign data.
- `queued_persistence`: terminal committed before Handler drain, direct AttemptBoundary replacement, stale identity-scoped cancellation through production control, then drain. The committed row survives while stale UI is suppressed; replacement remains deliverable. Existing accepted subscriber/view/init race coverage is linked in the envelope.
- `partial_clear`: actual existence observations after purge failure. Some files are already removed while SQLite still retains rows; no fictional filesystem transaction is claimed.
- `clear`: actual new participant ID, independent empty tables, both export roots and legacy residue purged, unrelated sentinels retained.
- `reopen`: actual stable replacement identity and independently queried empty tables after closing all owners/helpers and reopening with a fresh real preference object.
- `delivered_events`: exact strings, not manufactured Flutter channel logs.

Export path strings in control responses are the original isolated native paths. The runtime fixture is deliberately disposed; consumers read the exact retained export artifact bytes through this manifest, not those historical scratch paths.

## Native seams and isolation

The real MethodChannel registration calls `controlHandler(owner)`, the same callable invoked by the host harness. Locking, fixed error-code handling, permission check and owner rejection remain in that callable. This is not a BinaryMessenger registration/startup test.

Production initialization uses the accepted A2b transaction with real SessionManager, DataExporter and BenchmarkMode; VisionEngine construction uses fake owned detector/interpreter handles and synthetic asset bytes. Attempts are started/replaced directly through the production AttemptBoundary because the bare Activity has no safe permission context. Terminal handling, persistence, posted delivery, ACK, cancellation, assessment/history/session/identity/export/clear controls are actual production code. No default application participant stores are opened.

The export database acquisition is explicitly bound to the initialization factory. Android production still uses application context. Injected factories without an export acquisition fail closed rather than falling back. The temporary export helper closes on success and failure. The fixture isolates internal/external/database/preferences roots, both database-open overloads, application-context return, unique preference XML names, helper ownership and sentinels. It uses real SQLite and Android SharedPreferences implementation, not a hand-authored persistence model.

## Reproduction

From the repository root, choose a new label and an absolute **nonexistent** destination whose parent exists:

```sh
python3 benchmarking/study_evidence/20261015/a3a/run-recovery.py NEW-LABEL jvm \
  com.kumpas.kumpas_app.HostStudyFlowTest \
  -Pkumpas.hostFixtureDir=/absolute/new/destination
```

The runner uses cached JDK17/SDK/Gradle in offline mode, session scratch TMPDIR and the shared `kumpas-gradle.lock`. It refuses to overwrite logs, snapshots XML while holding the lock, records commands/exits and prints the exact generated root/manifest from actual JVM stdout. Ordinary full JVM execution has a safe scratch output default and no external fixture precondition.

Fresh full verification command in `full-handoff-3`:

```sh
./gradlew --offline :app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin --rerun
```

Both target tasks have exact executed task lines. This is instrumentation **source compilation only**, not device execution.

## Verified results and limits

Focused 129/129; explicit producer suite 5/5; full JVM 170/170; zero failures/errors/skips in each final run. All 82 protected files and all 8 latest accepted A2a hashes match. The authorized A2b MainActivity/factory extraction is intentionally changed; its exact preimages match the latest A2b acceptance, and final postimages/delta are frozen separately. Existing A2b resource/subscriber tests remain unchanged and pass.

The schema regression `feedback-schema-red` exposed an invalid constructed feedback item (textual severity/missing consumer fields). Its failure was captured before fixing the synthetic input. The final input has numeric severity and required hand/prompt strings; assertions run before successful manifest publication. Earlier shallow native GREEN artifacts were superseded, not repurposed. The preserved failing producer run contains no success manifest.

No Dart, collector, model, training, math, XP or layout source changed. No emulator/phone/ADB/install/download/default participant stores/commit/reset/clean/worktree operation. No installed E2E, actual detector release, recognition accuracy, physical performance or human/study acceptance. Parent review and A3b consumers remain separate work.
