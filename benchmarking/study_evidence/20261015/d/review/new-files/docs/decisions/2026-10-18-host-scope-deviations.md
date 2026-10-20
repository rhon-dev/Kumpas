# Proposed host scope and architecture decisions

Date: October18,2026. **Status: PROPOSED / APPROVAL PENDING** for every proposal below. This is a decision request, not a stack amendment, retraining authorization, numerical promotion policy or human-study approval. PRD §4/§6 remain governing. PM, adviser and expert fields are intentionally blank. Parent whole-package review is also pending.

## D-01 — Shipped split landmarkers versus locked Holistic

**Observed:** PRD names MediaPipe Holistic. The shipped `VisionEngine.kt` uses PoseLandmarker and HandLandmarker; the deployed classifier consumes30×258 no-face features. Existing `pipeline_parity.py` and the accepted B1 external fixtures distinguish Python Holistic, sampled-PNG tracking, stored full-video preprocessing and historical Android replay schemas. B1 six references are prepared host artifacts, not new Android parity or anatomy evidence. Model/reference bytes and normalization math were not changed in Package D.

**Proposed decision:** document the shipped split-landmarker/no-face path as a scoped architecture deviation pending explicit PM/adviser approval, with expert/anatomical and actual camera parity gates retained. Keep the shipped model unchanged while the decision is evaluated.

**Alternatives:** reject the deviation and separately design/authorize a Holistic migration; or retain the present implementation strictly as a research prototype without claiming locked-stack compliance. A migration requires its own compatibility, model, performance and expert evidence; host self-comparison cannot approve it.

**Consequences and affected gates:** Phases4–6/9/9a and model provenance; no claim that matching feature dimensions proves anatomy, equivalent detector tracking or recognition robustness. Sparse-frame versus full-video differences are not automatically normalization defects.

PM decision: __________  Adviser decision: __________  Expert record: __________  Date: __________

## D-02 — Historical local training versus locked Colab

**Observed:** PRD specifies Colab; historical experiment records name local M1/TensorFlow2.19.0. The approved October15 host design permits additive tooling and validation-only diagnostics, not actual retraining. Existing `train_cnn_lstm.py` writes the protected historical protocol log by default. No isolated bounded experiment runner has been implemented; host09 is not complete. B2's actual150 validation predictions/model are retained incomplete diagnostics, not a new training campaign.

**Proposed decision:** obtain an explicit historical-environment deviation decision separately from any future local-training permission. If experiments are later authorized, first freeze parameters, resource budget, output/log isolation and unchanged validation-only selection; implement and review an exclusive bounded runner before training. Preserve the proposed at-most-two sequential single-factor variants,60epoch/batch32/patience15/15-minute-per-run limits only as unapproved proposal details, not existing enforcement.

**Alternatives:** require all new training in the governed Colab environment; decline new experiments and retain the current prototype with its limitations. Neither option repairs previously consulted test data or establishes signer independence.

**Consequences and affected gates:** Phases2–4/9a, host09/10 and reproducibility. Local dependency drift (including Keras version differences) is disclosed; no automatic promotion, sweep expansion, protected-log rewrite or reused-test tuning is permitted. A green synthetic conversion test is not permission to convert a real model.

PM historical-deviation decision: __________  Adviser decision: __________  Separate training/budget authorization: __________  Date: __________

## D-03 — Local-only study storage/export; no implied cloud approval

**Observed:** the current app uses local SQLite and explicit export/purge mechanisms. A1/A2/A3 host tests exercise isolated synthetic persistence, publication, cache behavior and reopen. They do not operate default participant stores or prove one installed continuous flow. PRD makes Firebase/backend conditional on PM approval; no such approval is supplied here.

**Proposed decision:** retain local-only capture/export as the current technical study-tool boundary, contingent on separate privacy/consent/retention and actual-device authorization. Do not infer cloud sync, accounts, backend or participant collection permission from accepted host software.

**Alternatives:** separately approve/design a minimal backend and its privacy, ownership, transfer and failure contracts; or defer participant use until all study decisions are recorded. Exporting a local copy does not authorize transferring it externally.

**Consequences and affected gates:** Phases8/9/11, data lifecycle and researcher handoff. App-managed purge is not forensic erasure and does not delete external researcher copies. Physical installed export/delete/reopen and partial-failure behavior still require separately authorized evidence.

PM scope decision: __________  Privacy/consent/retention record: __________  Device/participant authorization: __________  Date: __________

## D-04 — Questionnaire export versus separate human-rated rubric

**Observed:** the legacy exporter serializes nested sessions/attempts and JSON-encoded assessment responses. Current pre/post confidence and `signsKnown` are1–5 self-reports, not a measured sign count. The post questionnaire is SUS-labelled but wording/translation validity is not established by its array length. C2 validates explicit synthetic exports and emits safe descriptives; it does not score human performance. A1 made optional feedback optional while retaining required-answer checks. A3 transport fixtures with dummy responses are not questionnaire-validity fixtures.

The pending study design proposes four0–3 dimensions (handshape/orientation/motion/timing), ten expert-selected signs, two-rater subset checks and named within/between-group analyses. It does not supply approved anchors/sign list, rater/blinding/adjudication, missingness, repeated-assessment policy, group joins/withdrawal, effect-size denominator, Welch/equal-variance choice, sidedness, intervals or multiplicity rules.

**Proposed decision:** preserve the legacy technical export adapter; define a separately versioned human-observation sidecar only after explicit instrument/method approval. Keep human scoring, SUS scoring, real-data participant processing and inferential acceptance blocked. Never substitute confidence, geometric score, mastery, XP or ordinal questionnaire responses for the human rubric.

**Alternatives:** separately authorize an app schema/UI change to capture an approved human instrument; or collect an approved paper/external instrument with an approved pseudonymous join. Neither alternative is implemented or approved by this record.

**Consequences and affected gates:** Phases11/12 and host11/12. Missing observations remain absent/null with reasons, not zeros; repeated phases stay ambiguous until policy exists. Synthetic descriptive success proves software behavior, not learning benefit or statistical validity. Consent/group/withdrawal cannot be inferred from missing records.

Instrument/sign-list approval: __________  Rater/missingness/join approval: __________  Statistical plan approval: __________  Ethics/participant authorization: __________  Date: __________

## Already decided policy and an explicitly undecided packaging observation

Do not reopen the approved UUID-receipt ownership and generated/structured-metadata policy. Its authority is `benchmarking/study_evidence/20261007/controller/owner-approved-review-closure-brief-2.md`; the later A/follow-up acceptances apply bounded repairs without inventing physical/study approval.

Fresh October18 release inspection observed Flutter/app ARM64 only, with dependency libraries in arm64-v8a/armeabi-v7a/x86_64. Historical three-ABI packaging consistency passed and strict ARM64-only expectation rejected. This is not an approved packaging policy or proof of a configuration defect. Any narrowing of dependency ABIs or signature/ELF/runtime requirements needs its own decision and evidence; no Gradle/application configuration changed in D.

## Evidence and approval discipline

Use `docs/host-completion-2026-10-18.md`, `docs/host-reproducible-handoff.md`, October15 design/plan/discovery audits, the named controller acceptances, `d/historical-readback.json`, `d/artifact-readback.json` and the frozen whole-change review package. Historical B1/B2 source identities remain bound to before snapshots after later comparator/helper/test hardening; current-capture hashes are not retrospective preregistration. Full B2 provenance remains blocked134 DATALESS source pairs. Parent approval of host-only work cannot supply any blank human decision above.
