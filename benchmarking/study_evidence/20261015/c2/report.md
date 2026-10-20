# C2 execution report

Status: implementation in progress; not accepted. Independent review is required. Source audit and acceptance are in taskbrief.md. No participant data has been opened.

## Completed bounded implementation

Added `evaluation/__init__.py`, `legacy_export.py`, `synthetic_descriptive.py`, `export_cli.py`, their three `test_*.py` modules and `README.md`. No preexisting application, native, Dart, training, benchmark or accepted C1 source was edited. Helpers/evidence live only under this C2 directory. The detailed source-derived contract, matching denominators, trust boundaries and runnable commands are in `evaluation/README.md`.

Host11 legacy-questionnaire validation and host12 synthetic counts/completeness/pair-availability/frequencies are **implemented and eligible for bounded independent review, not accepted by this worker**. The full human rubric and inferential portions remain blocked. No human scoring, SUS total, confidence-as-outcome, group allocation, consent inference, imputation or inferential statistic was added.

## Actual execution

- Vertical public-behavior RED/GREEN logs: slices1–8 in the append-only command ledger. Initial adapters returned fixed unsupported results so RED was an actual assertion failure, not missing imports. Strict/schema, matching, CLI, closed-session counts, strict JSON arguments/duplicate inputs, owned publication collision and existing normalized producer ranges each have preserved failing checks before their implementation. Additional exact-type/nonfinite/optional/feedback/FIFO/symlink/publication-fault cases are labelled coverage, not invented repair RED.
- Final authoritative suite: `slice8-normalized-green-final.log`, **16 tests, no failures/errors/skips**, existing `/opt/homebrew/bin/python3.11 -B -E`, unittest discovery. Test methods contain additional adversarial matrices; the reported 16 is the unittest method count, not an inflated subcase count. No broad app/native/training suite was executed for this additive package.
- Final authoritative CLI evidence: `synthetic-cli-final-bound/`. Four actual CLI invocations: describe/validate valid exits0, invalid exits2. Five generated synthetic exports represent paired, pre-only, post-only, repeated-phase and no-assessment cases. Independently recomputed totals: **5 exports, 5 synthetic participants, 4 sessions, 4 attempts, 7 assessments**; matching has exactly one participant in each of paired/unmatched-pre/unmatched-post/ambiguous/no-assessments. All reported known-field frequencies, completeness and input/output hashes were independently recomputed without the descriptive implementation. Invalid input left no output directory or success manifest. Fixed diagnostic outputs do not contain fixture private-text canaries, participant UUIDs or input paths.
- The final run's `independent-cli-verification.json` binds eight source/helper hashes and all output hashes. Earlier `synthetic-cli`, `synthetic-cli-final` and `synthetic-cli-reviewed-snapshot` are retained intermediate runs; final-bound supersedes their source-acceptance role without rewriting their bytes.
- Read-only audit of the accepted A3a isolated native producer: exact parent binding/manifest digest, successful five-test producer XML, success ledger and all42 source hashes verified before the three named synthetic exports were read. Nonempty external/internal exports each have1 session/1 attempt/2 assessments but use transport-only `synthetic`/`stage` answers; `REQUIRED` rejection is correct. The empty reopened export validates. This does not claim a newly executed native suite, UI-origin questionnaire fixture, continuous installed flow or an app defect. Native fixture/schema mismatch is a limitation to retain, not authority to edit accepted A3a source.

## Final output SHA-256

| Artifact under final-bound | SHA-256 |
|---|---|
| SYNTHETIC-001/report.json (describe) | `5c2b167c471e24ff6a6aed311c22e180940307d465a110b5e397802a9d9a5380` |
| SYNTHETIC-001/manifest.json | `f162ae15e575a64f722335ec67393babf3232ffde7ccfce6dc5a54f145842f96` |
| SYNTHETIC-002/report.json (validate) | `b9f165e13444def9fcc4b413b79e110b24e871bbd755834ac9848e1fbd6af9aa` |
| SYNTHETIC-002/manifest.json | `b50563abf4b7dbc664e07f020576f51ceb41e0bfd45e5b349e5f527825f5aee3` |

## Issues and preserved failed checks

The first CLI test root inherited system TMPDIR (`/var/...`, a symlinked ancestor) instead of the declared Hermes scratch root. Symlink rejection correctly blocked it; tests were corrected to explicit Hermes scratch, and temporary synthetic directories were cleaned by their test owners. No store was opened. Initial top-level unittest discovery required an additive `evaluation/__init__.py`; its importability error is retained and is not feature RED evidence.

A later final-suite run found a stale pre-ownership mock signature and missing collision test relative to the prior15-test GREEN log. The regression was restored, the signature updated, and final16-test plus source-bound CLI runs passed. The cause of that stale postimage was not established. Parent must match the final-bound source hashes rather than trusting any earlier GREEN log.

The first preservation helper compared protected hash strings to the baseline's whole `{expected,actual}` objects, falsely reporting all82 mismatches. `after.json` is retained as erroneous diagnostic evidence, **not the preservation verdict**. Corrected `after-verified.json` checks `expected` digests and the separately captured before hashes. It reports **1,248 preexisting repository source/evidence files unchanged; all82 protected originals unchanged against both before and expected baseline**. This inventory excluded C2's new evidence and installed stores. No reset/stash/commit/download/device command or real participant processing occurred.

## Remaining decisions and review

The UI/export has no human rubric observations, raters, instrument version, allocated group, consent/withdrawal status or assessment-to-session foreign key. `signsKnown` is an ordinal self-report, not a measured sign count. The local SUS-labelled ten-item text is not accepted as a validated standardized questionnaire merely because its response array has ten items. Repeated phases are ambiguous; absence remains absence. Active summaries can lag, unlike recomputed root counts and closed-session counts.

Human instrument/anchors and selected signs, rater/blinding/adjudication, allocation/join including control participants without installs, repeated/missing/withdrawn policy, wording/translation, consent/retention and detailed statistical policy remain blocked decisions. No p-values/effectiveness or physical/runtime acceptance is available. Parent independent verification plus specification and quality review are still required before accepting the bounded host11/12 subset. C1's accepted status and its low-priority publication-test follow-up remain untouched.

## Final duplicate-source preservation

Final Git inventory exposed a newly appeared `evaluation/test_export_cli 2.py`, absent from the before inventory and byte-identical to the restored canonical test (`a3de3750f4acdcaa2938c2e1f9de97e803f502ed45aa541bcaec95c07d6b587b`). Its origin is not established; the cloud-backed checkout and earlier stale postimage are observations, not proof of a cause. The duplicate was preserved by an exclusive move to `c2/quarantine/test_export_cli-duplicate.py`, without altering the canonical file or any preexisting file. It is not an additional independent test suite. `handoff-snapshot-final.json` supersedes the earlier handoff snapshot's inventory location; the older snapshot remains historical evidence. Final-bound source hashes remain authoritative for executable code.


