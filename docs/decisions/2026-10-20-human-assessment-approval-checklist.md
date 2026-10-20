# Human assessment approval checklist

Prepared: October 20, 2026.
Status: DRAFT — ALL DECISIONS AND APPROVALS PENDING.
Purpose: Give the PM, adviser, FSL expert and applicable ethics/privacy authority a concrete decision record for host-11. This preparation does not approve an instrument, authorize participant processing or close a study gate.

## Meeting preparation

Bring these existing records:

- `docs/PRD.md`, particularly scope, roles, evaluation phases and privacy requirements.
- `docs/decisions/2026-10-18-host-scope-deviations.md`, D-03 and D-04.
- `evaluation/README.md`, for the actual legacy export contract and synthetic-only limits.
- `docs/phase10-expert-validation-protocol.md`, for the separate reference/prompt validation record. A blank template is not an expert approval.
- `docs/selected-50-signs.md`, as the application vocabulary, not an approved assessment subset.

The existing proposal mentions ten signs and four 0–3 dimensions. Those details remain proposals. This checklist does not adopt them, select signs, define anchors or choose statistical tests.

For every item below, record the decision text or an attached versioned document, responsible approver, decision date and disposition: pending, approved, rejected or revision required. Do not infer approval from attendance or a checked preparation box.

## 1. Instrument identity and sign selection

- [ ] Name the instrument, version and intended construct.
- [ ] Define the tasks participants perform, the sign list and exact label/class identities.
- [ ] Specify instructions, demonstration access, practice exposure and attempt limits during assessment.
- [ ] Define comparable pre/post conditions and any permitted accommodation.
- [ ] Identify FSL expert validation evidence for selected signs and assessment reference material.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 2. Dimensions, scales and observable anchors

- [ ] Approve or revise each performance dimension separately.
- [ ] Define every permitted score with observable anchors and examples.
- [ ] Define how unobservable performance, missing hands, technical capture failure and incomplete attempts are recorded.
- [ ] Decide whether dimensions/signs may be aggregated, including weights, denominator and interpretation.
- [ ] Separate an observed zero from a missing or unrateable observation.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 3. Raters and disagreement

- [ ] Name rater eligibility, training and calibration requirements.
- [ ] Specify which performances receive independent ratings and how that subset is selected.
- [ ] Define blinding to participant group, pre/post phase and other raters' results.
- [ ] Define disagreement handling, adjudication and preservation of original ratings.
- [ ] Approve any reliability calculation, its inputs and interpretation.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 4. Missing, repeated and withdrawn observations

- [ ] Define missingness reasons and any permitted retry policy.
- [ ] Decide how repeated pre/post records are handled without silently choosing the latest.
- [ ] Define withdrawal handling for records, exports, analysis and any permitted retained audit information.
- [ ] Define inclusion/exclusion rules and when those rules become fixed.
- [ ] Decide any imputation policy explicitly. Until then, missing values remain missing.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 5. Participant, group and assessment linkage

- [ ] Define pseudonymous identity creation and who holds any identity linkage.
- [ ] Define experimental/control allocation and how control participants enter records without assumed app sessions.
- [ ] Specify the explicit join between human assessments, participants, group and phase.
- [ ] Define collision, mismatch, repeated-export and withdrawal handling.
- [ ] Select approved storage: a versioned external observation record or a separately authorized app change.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 6. Questionnaire wording and interpretation

- [ ] Approve exact wording, language, translation and response options.
- [ ] Separate optional fields from required answers.
- [ ] Confirm that `fslConfidence` and `signsKnown` are ordinal self-reports, not demonstrated performance or a measured sign count.
- [ ] Resolve whether the SUS-labelled items constitute an approved instrument. Ten items alone do not establish standardized SUS scoring.
- [ ] Approve any questionnaire scoring separately from the human performance instrument.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 7. Consent, access, retention and transfer

- [ ] Identify the required ethics/privacy approval and actual authorization record.
- [ ] Approve consent materials, withdrawal process and eligibility, including any age-related requirements.
- [ ] Specify collected data, storage locations, authorized roles and retention periods.
- [ ] Specify export/transfer approval, permitted recipients and handling of external copies.
- [ ] Define deletion responsibilities. App-managed deletion does not erase researcher copies or prove forensic erasure.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 8. Analysis plan

- [ ] Define primary/secondary outcomes and analysis populations.
- [ ] Specify within/between-group questions and the exact approved analysis method for each.
- [ ] Define sidedness, confidence intervals, assumptions and any variance/test-selection policy.
- [ ] Define effect-size calculation and denominator, multiplicity handling and reporting rules.
- [ ] Bind missing/repeated/withdrawn handling to section 4 and group linkage to section 5.
- [ ] Freeze the approved plan before outcome-dependent choices. Record later amendments without rewriting historical decisions.

Decision / attachment: ____________________
Approver(s), date, disposition: ____________________

## 9. Final disposition and implementation release

Instrument/version and attached sign list: ____________________
Scoring anchors and rater procedure/version: ____________________
Data lifecycle and linkage procedure/version: ____________________
Analysis plan/version: ____________________
PM name, decision and date: ____________________
Adviser name, decision and date: ____________________
FSL expert name, decision and date: ____________________
Applicable ethics/privacy authorization reference and scope: ____________________
Unresolved items and responsible person: ____________________

Separate authorization decisions:

- Synthetic implementation of the approved instrument: PENDING.
- Participant collection/processing: PENDING.
- Human scoring and inferential analysis: PENDING.
- Device installation/runtime work: PENDING; not authorized by this checklist.

## Completion and next steps

1. The owner obtains written decisions and attachments from the responsible authorities. The assistant cannot supply those approvals.
2. Resolve every applicable section; record any non-applicable item with its approved rationale.
3. After explicit development authorization, implement only approved rules using isolated synthetic records and regression tests.
4. Independently verify the implementation against the approved instrument and plan. Technical schema acceptance does not establish instrument validity.
5. Keep host-11 open until the approved procedure and any required implementation acceptance exist. Checklist preparation alone does not complete host-11.

Do not substitute model confidence, geometric match, mastery or XP for human learning outcomes. No actual participant records were used to prepare this document. Experiment-runner work remains deferred; this checklist does not authorize training, model conversion or deployment.
