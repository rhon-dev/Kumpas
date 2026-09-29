# Mastery rule — acceptance design

**Decision:** The project owner confirmed on September 29, 2026 that a target sign is mastered only when an attempt both has `overallMatch >= 0.8` and has `recognizedAsTarget == true`.

## Intent and scope

Mastery is a per-target-sign, history-derived status, not a new classifier or change to feedback scoring. One qualifying attempt suffices; later nonqualifying attempts do not undo it. The existing rule that history is local remains unchanged. This change applies consistently to the overall mastered-sign count, category mastered/total and completion status, and selection of the next unmastered sign in the Learn screen. Other displays based on match score alone—XP, the numeric score color, and feedback-sheet messaging—remain separate concepts and are not changed by this decision. A separate product decision is required before interpreting XP or the feedback sheet as evidence of mastery.

## Design

Provide one named predicate for the mastery decision on an `AttemptResult`, shared by `LearnerStats.fromHistory`, `LearnerStats.categoryProgress`, and the Learn screen's next-sign selection. The predicate must inspect the *same attempt* for both the threshold and target recognition; a high-score mismatch cannot combine with a low-score correctly recognized attempt to count as mastery. The sign is credited to its `targetClass`, and repeated qualifying attempts count that sign only once. Keep category totals derived from the sign library rather than attempted signs.

The rule uses the existing `recognizedAsTarget` value emitted by the native pipeline; this design does not alter how recognition or `overallMatch` is calculated. If that value is false because classification is uncertain or wrong, the attempt is not mastery, even if its match is high. Historical attempts are recomputed from the same stored fields when the UI loads; no migration is needed.

## Acceptance criteria

1. `overallMatch == 0.8` with `recognizedAsTarget == true` counts; a lower score or false recognition does not.
2. A high-score attempt recognized as another sign does not raise overall mastery, category progress, or cause the next-sign selector to skip its target.
3. Two attempts for one target cannot be combined across the predicate: high-score mismatch plus low-score recognized-as-target is still unmastered.
4. A later qualifying attempt masters that target exactly once; category progress and next-sign choice update consistently. A later nonqualifying attempt does not revoke mastery.
5. Tests exercise the actual Dart stats and Learn-selection code, including a mixed-sign category and empty history. Existing XP and feedback-score display behavior remains unchanged.
6. The documented acceptance rule and regression tests are reviewed against the implementation; no model, Kotlin feedback algorithm, export schema, or unrelated working-tree edits are changed.

## Verification

Run the focused Dart/Flutter tests with a demonstrated failing mismatch case before the implementation change; then run the focused and full app test suite, format/analyze affected Dart files, and inspect the diff for scope and unrelated edits. This is a code-path acceptance test, not validation of pedagogical learning or physical-device recognition.
