# C2 independent specification and quality review

## Verdicts

- **Specification: APPROVE, bounded host11/host12 subset only.** The explicit-file legacy-questionnaire validator and synthetic descriptive/matching CLI satisfy the approved Package C subset. Full human scoring, study tooling and statistical acceptance are not complete or authorized.
- **Code quality: APPROVE WITH MINOR CONCERN (L1 below).** No blocking correctness/privacy defect was found in the reviewed scope. The concern is durable regression coverage, not a reproduced implementation failure.
- **Acceptance remains the parent's decision.** This independent review does not close participant authorization, physical/runtime, human-instrument or inferential gates.

## Scope and source identity

Read PRD, phase gates, approved host-completion design, Package C plan, C2 task brief/report, evaluation README, parent verification and complete postimages of all eight evaluation files. Review did not rely on old HEAD or only changed diff hunks. The delivered `c2-review-package-1.diff` contains all eight paths; current file hashes match `controller/c2-parent-verification-1.json`. The final-bound and parent CLI bindings also match current executable source and their exercise helper. The README is separately bound by the parent's eight-file manifest, not by the executable/helper CLI manifest.

| Reviewed file | SHA-256 |
|---|---|
| `evaluation/README.md` | `595dee123aad04571170a2aab10faec119f346eec65d27a23a2a4c8b125fc3db` |
| `evaluation/__init__.py` | `268e24bb8d8792213f2773e72ee3529ab85aeb47bd4075cae338f29be5799536` |
| `evaluation/export_cli.py` | `2975b0e7a0f2dd13f720166fdc85fbd4f7ea538b599d11c60f42c1bd453b18c7` |
| `evaluation/legacy_export.py` | `170760c62bc54076bd119237d3eb8cddec957ed19abfb9e74f1ee2fea353298f` |
| `evaluation/synthetic_descriptive.py` | `fc780891c71944154328380c7ce11952faf9c05638c95b4ee94d0baeaea22cde` |
| `evaluation/test_export_cli.py` | `a3de3750f4acdcaa2938c2e1f9de97e803f502ed45aa541bcaec95c07d6b587b` |
| `evaluation/test_legacy_export.py` | `8a6eb9c03cef606bacf62f716f3a0a8eb82c38ec6bafdd4ba018123ec130a939` |
| `evaluation/test_synthetic_descriptive.py` | `782e0d7184594348e8f1433ecbb4e0dd2d5243090baec1708e64ae0f08fcd3a0` |

## Actionable finding

### L1 — Low, nonblocking: persist the two critical ownership/snapshot probes as regressions

**References:** `evaluation/test_export_cli.py:36–47,79–97,115–124`; implementation `evaluation/export_cli.py:58–84,105–119`.

The committed-to-review test postimage checks publication failure, existing-output preservation, manifest collisions before acquisition, and ordinary digest equality. It does not permanently regress (a) replacing a manifest *after the publisher acquired its inode*, then failing, or (b) changing the input pathname after bytes were snapshotted but before publication. These are distinct invariants central to the documented ownership and same-byte binding contract.

**Executed reproduction/coverage:** in a fresh synthetic scratch root, wrapped `_write_read` to finish the owned manifest write, renamed that inode to a retained filename, created a different-inode sentinel at `manifest.json`, and raised `Rejected('OUTPUT_READBACK')`. `main` returned 2 with the fixed code and preserved the unowned sentinel. Separately wrapped `_publish` to replace the input file with invalid JSON after snapshot/validation: `main` returned 0 and its manifest still hashed the original input bytes used by the report. Both implementation behaviors are correct; these are coverage-only GREEN probes, not repaired defects or extra unittest methods.

**Follow-up:** add these deterministic cases to the canonical CLI test module in a separately authorized slice. Keep the displaced owned inode alive in the cleanup test so inode reuse cannot make the test nondeterministic. No source change is requested as a prerequisite for this bounded approval.

## Contract/specification assessment

- **Actual legacy shape, not guessed UUID-everywhere:** audited `DataExporter.kt:74–111`, `SessionDatabase.kt:48–84,136–172,247–265,301–310` and assessment save/UI code. Attempt/assessment primary keys are positive integers, participant/session identities are UUIDs, nested relationships are enforced, and responses/feedback are encoded JSON strings. The strict adapter has no invented schema-version field. Unknown fields fail closed rather than guessing migration semantics.
- **Strictness/privacy:** `legacy_export.py:24–78,86–108,111–194` rejects duplicate keys in outer/encoded JSON, nonfinite/overflow float literals, boolean/integral-float integer substitutions, malformed containers, missing/unknown fields, duplicate IDs, foreign relationships, wrong phases, invalid ranges and root count mismatches. Errors contain fixed codes, and descriptive/CLI errors add input indexes rather than values, UUIDs or private paths. Feedback strings retain existing consumer types without invented linguistic rules.
- **Requiredness and normalized producer bounds:** `assessment_screen.dart:35–76,201–242,284–295` supports required 1–5 ordinal answers, optional demographics/feedback, and ten post items. `FeedbackEngine.kt:108–117,120–141,144–178,181–209,253–255` plus Dart `models.dart:18–32` support normalized technical values and required feedback strings. These are technical validation bounds, not human rubric scoring. Active session summaries can lag; closed counts and scoped root totals are reconciled, without inventing an average tolerance policy.
- **Descriptive denominators/matching:** `synthetic_descriptive.py:8–73` rejects an invalid batch before returning frequencies and rejects duplicate participant exports. One explicit pre plus one post gives paired availability; repeated phases remain ambiguous, single phases unmatched, and no assessments stays a separate category. No newest-record selection or timestamp-derived phase exists. Matching denominators are unique participants; frequencies and demographic completeness use assessment records, including valid repeated phases. Feedback completeness uses only post records, with empty-string a subset of present, not an additional disjoint denominator. Optional absence is never imputed as zero. Per-phase/item frequency denominators are recoverable from their counts and are documented in README:20–26.
- **Scientific limits:** signsKnown is an ordinal self-report, not a measured count. Local SUS-labelled wording is not treated as a validated standardized instrument. No SUS total, improvement score, human score, confidence-as-outcome, effect size, p-value, consent/group/withdrawal inference, rater aggregation or inferred missingness policy is implemented. UNATTESTED validation is capability, not processing authorization; descriptives require SYNTHETIC.
- **Filesystem/publication:** `export_cli.py:17–53,58–89,94–120` requires an explicit absolute existing root, explicit contained relative inputs and a restricted output label; walks directories descriptor-relatively without symlinks/dot traversal; opens input nonblocking and rejects nonregular/FIFO inputs before reading; bounds each file to 16 MiB. Input snapshot bytes feed validation, descriptions and digest computation. Publication uses exclusive directory/file creation, fsync/file readback, fixed errors, and inode-matched owned-manifest cleanup, without overwriting existing outputs. Partial owned diagnostic directories/reports may remain, as documented. Trusted isolated root, no hostile directory relocation and no directory-fsync/power-loss durability are explicit limits, not newly claimed guarantees.

## Fresh reviewer execution and independently checked evidence

Executed from the exact repository with existing `/opt/homebrew/bin/python3.11 -B -E` and explicit Hermes scratch TMPDIR. No dependencies were installed, no app/default participant store was opened and no native/device/inference process was run.

1. **Fresh canonical suite:** `-m unittest discover -s evaluation -t . -p 'test_*.py' -v` returned exit 0: **16 tests, zero failures/errors/skips**. This is the canonical test-method count; adversarial matrices and the quarantined duplicate are not counted as additional tests. This independently agrees with, rather than merely repeats, the parent's saved 16-test statement.
2. **Fresh reviewer synthetic CLI:** copied only the five named synthetic parent input snapshots into a new temporary scratch root. Actually executed describe-valid, validate-valid, describe-invalid and validate-invalid: **exits [0,0,2,2]**, empty stderr, no private canary/root echo, and no output directory on invalid input. All four successful `report.json`/`manifest.json` files were byte-identical to the saved parent/final-bound files.
3. **Independent recomputation:** read both `c2/synthetic-cli-final-bound/` and `c2/synthetic-cli-parent-1/`; recomputed using stdlib JSON/Counter rather than the descriptive implementation: **5 exports, 5 participants, 4 sessions, 4 attempts, 7 assessments**; one participant in each matching category; all structured field/item frequencies and optional-field completeness agreed. Checked every input index/hash and report/manifest digest, source/helper hash, invalid saved diagnostic and absent invalid output. The temporary fresh run's bytes matched these recomputed artifacts.
4. **Extra deterministic probes:** immutable-input snapshot and replaced-owned-inode failure cases described in L1 both passed. Synthetic temporary roots were cleaned by their owners. The scratch probe script is `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/c2-independent-review-probe.py`; it is outside the repository, checks resident regular files before reads, and returns exit 0. These are reviewer probes, not a fresh broad app/training suite.

Verified output SHA-256 values shared by final-bound, parent, and fresh reviewer publication:

| Artifact | SHA-256 |
|---|---|
| `SYNTHETIC-001/report.json` | `5c2b167c471e24ff6a6aed311c22e180940307d465a110b5e397802a9d9a5380` |
| `SYNTHETIC-001/manifest.json` | `f162ae15e575a64f722335ec67393babf3232ffde7ccfce6dc5a54f145842f96` |
| `SYNTHETIC-002/report.json` | `b9f165e13444def9fcc4b413b79e110b24e871bbd755834ac9848e1fbd6af9aa` |
| `SYNTHETIC-002/manifest.json` | `b50563abf4b7dbc664e07f020576f51ceb41e0bfd45e5b349e5f527825f5aee3` |

## Guarded native synthetic artifact cross-check

Before reading the three native exports, independently verified the exact `a3a-acceptance-and-consumer-binding.json` manifest digest/run identity, synthetic-origin/success fields, successful producer XML (**5 tests, zero failures/errors/skips**), successful parent ledger label and **42 current source hashes**. Then checked each named artifact's length/hash and validated only those synthetic byte snapshots.

`external-export.json` and `internal-export.json` correctly returned fixed `REQUIRED`: the transport fixture deliberately has dummy synthetic/stage responses, not UI questionnaire answers. `reopened-export.json` validated with zero sessions/attempts/assessments. This is historical accepted native-producer artifact inspection, **not** a newly executed native suite, native questionnaire UI validation, an application-defect finding or installed end-to-end proof.

## Preservation and historical evidence adjudication

- Independently rehashed **all 1,248 entries** in `c2/before.json`: unchanged. Independently matched **all 82 protected originals** to both the before capture and `controller/host-baseline.json` expected hashes. Corrected `after-verified.json` agrees. No file was skipped/hydrated to obtain those results.
- `after.json` is the explicitly erroneous historical helper result, not a competing preservation verdict. It compared digests against baseline objects; it is not used for approval.
- Quarantined `c2/quarantine/test_export_cli-duplicate.py` is byte-identical to the canonical final CLI test and is not counted as an additional suite. The canonical source hash matched before and after reviewer probes. Earlier stale source/duplicate origin remains unknown; no cloud/concurrency causation is asserted. Earlier CLI runs do not supersede final-bound source identity.
- Only this assigned report was changed inside the repository. Scratch synthetic probe code/temporary roots are outside it. No reset, stash, worktree, commit, installation, cloud hydration, participant processing, training, inference or conversion was performed.

## Remaining gates / handoff

Parent must adjudicate L1 explicitly, rematch the eight reviewed postimages and record bounded acceptance separately. The original host11 human rubric/instrument/sign anchors, rater/blinding/adjudication, allocation/control joins, repeated/missing/withdrawn policy, local wording/translation validation, consent/retention and statistical decisions remain blocked. Existing physical, live-signer, linguistic/anatomical and model gates are untouched. A3a native transport limitations and C1's separate accepted scope/follow-up remain unchanged.
