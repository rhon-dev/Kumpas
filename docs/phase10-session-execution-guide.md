# Phase 10 FSL Expert Validation Session — Execution Guide

**Status:** Ready to execute  
**Materials Prepared:** ✅ Complete  
**Next Action:** Schedule session with FSL Expert

---

## Pre-Session Checklist

### Materials Ready ✅

1. **Gold-standard clips extracted:**
   - Location: `../kumpas-data/gold_clips_for_review/`
   - Count: 50 numbered .MOV files (00 through 49)
   - Format: Sequential naming for easy playback

2. **Session protocol document:**
   - Location: `docs/phase10-expert-validation-protocol.md`
   - Content: Full 5-block session structure with 50-sign checklist

3. **Gate closure form:**
   - Location: `docs/phase10-gate-closure-form.html`
   - Format: Styled HTML ready for browser → PDF export
   - Status: Print-ready with signature blocks

4. **Demo report (reference):**
   - Location: `training/feedback/demo_report.md`
   - Content: 5 worked examples + prompt copy review items

5. **Gold standards manifest:**
   - Location: `training/feedback/gold_standards_manifest.json`
   - Status: All 50 entries marked "provisional — pending expert validation"

---

## Session Setup (30 minutes before)

### Equipment Setup

1. **Laptop for clip playback:**
   ```bash
   # Open the clips folder
   open ../kumpas-data/gold_clips_for_review/
   ```
   - Verify all 50 clips are present and play correctly
   - Test VLC or QuickTime player
   - Have slow-motion playback available (VLC: press `[` to slow down)

2. **Print materials:**
   - Gate closure form: Open `docs/phase10-gate-closure-form.html` in browser → Print to PDF → Print physical copy
   - Session protocol: Print `docs/phase10-expert-validation-protocol.md` for note-taking

3. **Laptop for note-taking:**
   - Have `gold_standards_manifest.json` open for live status updates
   - Have a text editor ready for capturing expert comments

4. **Optional: Live app demo**
   - If available, have the app running on emulator/device to show feedback in action
   - Not required, but can help expert understand context

---

## Session Execution Flow (90-120 minutes)

### Block A: Context Briefing (15 min)

**Your script:**

> "Thank you for joining this validation session. Kumpas is a mobile app that teaches Filipino Sign Language through real-time corrective feedback.
>
> Here's how it works: A learner signs in front of their phone camera. The app recognizes which sign they're attempting and compares their execution against a 'gold-standard' reference. Then it gives specific feedback like 'your right hand is too low' or 'check your thumb position.'
>
> Today's goal: Validate that our gold-standard references are linguistically correct FSL, and that our feedback messages make sense to a learner.
>
> The gold standards were selected automatically — we used an algorithm to pick the most 'typical' execution of each sign from our dataset. But typical doesn't always mean correct. That's why we need your expert review."

**Confirm understanding:**
- Does the expert understand what a gold standard is in this context?
- Do they understand that this is the thesis's core contribution (feedback, not classification)?

---

### Block B: Gold-Standard Clip Review (45 min)

**Process for each clip:**

1. **Play the clip** (full speed, then slow if expert requests)
2. **Ask:** "Is this a correct, complete execution of [SIGN NAME]?"
3. **Record rating:** PASS / ACCEPTABLE / REJECT
4. **Capture notes:** If REJECT or ACCEPTABLE, ask why

**Expert ratings guide:**
- ✅ **PASS** = This is textbook FSL; use as gold standard
- ⚠️ **ACCEPTABLE** = Minor variation but won't mislead learners
- ❌ **REJECT** = Wrong, incomplete, or would teach bad form

**Pacing:**
- ~50-60 seconds per clip (includes playback + rating)
- Prioritize completeness over speed
- If a clip is clearly wrong, expert can reject without watching full clip

**Live tracking:**
- Tally PASS/ACCEPTABLE/REJECT counts on protocol document
- Target: ≥45/50 approved (90% threshold)

---

### Block C: Prompt Copy Review (20 min)

**Review all 5 prompt templates** (see gate closure form Section B):

For each prompt, ask:
1. **Is the wording clear to an FSL learner?**
2. **Are there better terms we should use?** (e.g., "the model" vs "the example")
3. **Would this feedback be actionable?** (Can the learner fix their sign based on this?)

**Key questions to address:**

- **"The model" wording:** Should we say "the example" instead? (Affects prompts 1, 2, 5)
- **Orientation not actionable:** "Rotate your palm" doesn't say which direction. Is this okay, or do we need to add direction? (This would require code changes)
- **Motion grammar:** "right and lower" sounds odd. Should we say "to the right and down"?
- **Mirror convention:** When the learner sees "move left" on their mirrored selfie view, does that match their intuition?
- **Prompt volume:** In the worst case, 6 feedback items appear at once. Should we limit to top 3?
- **Language:** Should prompts be in English, Filipino, or both?

**Record revisions** in Section B of gate closure form

---

### Block D: Threshold Calibration (10 min)

**Show the demo report** (`training/feedback/demo_report.md`) with worked examples

**Ask expert:**
1. Do the triggered feedback items match what you would tell a learner?
2. Are there obvious errors that the system missed? (too loose)
3. Are there false alarms — feedback on signs that look correct? (too sensitive)

**Focus on:**
- FOUR vs FIVE example: Does handshape-only feedback make sense?
- TOMORROW vs YESTERDAY: Should motion feedback have triggered here?
- Timing example: Is 25% speed deviation worth flagging?

**Record assessments** in Section C of gate closure form

---

### Block E: Sign-Off (10 min)

**Review the session results:**
- Gold standards: __/50 PASS, __/50 ACCEPTABLE, __/50 REJECT
- Prompt copy: Approved as-is / Approved with revisions / Needs rework
- Overall: Is the system pedagogically reasonable?

**Expert fills out attestation** in Section D of gate closure form

**Sign the form** (expert + thesis author)

---

## Post-Session Actions

### Immediate (same day)

1. **Export gate closure form to PDF:**
   ```bash
   # Open form in browser
   open docs/phase10-gate-closure-form.html
   # Press ⌘+P → Save as PDF
   # Save to docs/phase10-gate-closure-signed.pdf
   ```

2. **Update gold standards manifest:**
   - Change status from "provisional" to "expert-approved" for PASS/ACCEPTABLE clips
   - Mark "rejected" for clips that failed
   - Commit changes to git

3. **Document remediation plan** (if any clips rejected):
   - Identify next-best medoid candidates for rejected classes
   - OR schedule fresh recording session with expert

### Within 1 week

4. **Apply prompt copy revisions** (if any):
   - Update `training/feedback/feedback_engine.py` (Python reference)
   - Update Kotlin port in `app/.../KumpasChannel.kt`
   - Re-run parity test to confirm implementations still match

5. **Update threshold values** (if expert recommended changes):
   - Modify constants in both Python and Kotlin implementations
   - Re-run demo report to verify new threshold behavior
   - Document rationale in design.md

6. **Update documentation:**
   - `docs/phase-gates.md`: Change Phase 10 gate status to ✅ CLOSED
   - `.kiro/specs/10-feedback-logic/design.md` §8 Open Items: Mark resolved items
   - Commit with message: "Phase 10 gate closed — FSL Expert validation complete"

---

## Gate Closure Criteria Met?

Phase 10 gate can close if:

- [x] Algorithm implemented (Python + Kotlin) ✅ Done
- [x] Parity test passed ✅ Done
- [x] Demo report with 5 worked examples ✅ Done
- [ ] ≥45/50 gold standards approved (PASS or ACCEPTABLE) — **Pending expert session**
- [ ] Prompt copy reviewed and accepted — **Pending expert session**
- [ ] Expert attestation signed — **Pending expert session**

**Current status:** Materials ready, session execution pending

**Blocking on:** Scheduling FSL Expert availability (90-120 minutes)

---

## Troubleshooting

### If <45/50 clips approved

**Options:**
1. Select next-best medoid from rejected classes (automated script can do this)
2. Schedule fresh recording session with expert (requires consent + provenance logging)
3. Reduce scope from 50 signs to 45 signs (would need PM approval + design doc update)

**Recommendation:** Option 1 (next-best medoid) is fastest path

### If prompt copy requires substantial rework

**Timeline impact:**
- Minor revisions (wording changes): 1-2 days (update both implementations + retest)
- Major revisions (new feedback dimensions): 1-2 weeks (algorithm changes required)

**Mitigation:** If major rework is needed, ask expert for "good enough for MVP" approval to unblock implementation phases, with documented plan for v2 improvements

### If expert is unavailable

**Alternative validators:**
- Thesis adviser (if they have FSL expertise)
- Another FSL instructor from the same institution
- Deaf community representative with FSL fluency

**Requirement:** Validator must have formal FSL linguistic expertise, not just conversational fluency

---

## Contact Information

**Thesis Author:** [Your name]  
**Expert Name:** [To be scheduled]  
**Adviser:** [Name]  
**Session Date:** [To be scheduled]

---

## Appendix: File Paths Quick Reference

```
Clips for playback:
  ../kumpas-data/gold_clips_for_review/00_GOOD_MORNING_clips_0_13.MOV
  ... (49 more files)

Session materials:
  docs/phase10-expert-validation-protocol.md
  docs/phase10-gate-closure-form.html
  training/feedback/demo_report.md

Source data:
  training/feedback/gold_standards_manifest.json
  training/feedback/feedback_engine.py

App implementation:
  app/lib/feedback_engine/kumpas_channel.dart
```

---

**Ready to execute.** Schedule the FSL Expert session and follow this guide.
