# Phase 10 Gate — FSL Expert Validation Session Protocol

**Purpose:** Close the highest-scrutiny gate in the Kumpas SDLC — validating that the corrective feedback logic produces linguistically accurate, pedagogically useful guidance.

**Duration:** ~90–120 minutes  
**Participants:** FSL Expert + Thesis Author  
**Date:** _______________  
**Expert Name:** _______________

---

## Pre-Session Preparation (Author)

- [ ] Extract the 50 gold-standard source videos from `clips.zip` to a viewable folder
- [ ] Prepare playback on a laptop (VLC or QuickTime, slowed playback available)
- [ ] Print or display this protocol document
- [ ] Have `training/feedback/demo_report.md` open for reference
- [ ] Prepare the app on emulator or device showing live feedback (if available)

---

## Session Structure

| Block | Duration | Activity |
|-------|----------|----------|
| A | 15 min | Context briefing + methodology overview |
| B | 45 min | Gold-standard clip validation (50 signs) |
| C | 20 min | Feedback prompt copy review (8 items) |
| D | 10 min | Threshold calibration discussion |
| E | 10 min | Wrap-up + sign-off |

---

## Block A: Context Briefing (15 min)

Explain to the expert:

1. **What Kumpas does:** A learner signs in front of the camera; the app recognizes the sign and compares it against a "gold-standard" reference to produce specific feedback on what to fix.

2. **What a gold standard is here:** One clip per sign, selected automatically as the most statistically typical execution from the FSL-105 dataset (medoid — the clip most similar to all others in that class). It is NOT necessarily the "textbook perfect" sign — it's the center of the dataset's distribution.

3. **What we need from the expert today:**
   - Confirm each gold-standard clip shows a linguistically correct execution of that sign
   - Flag any clip that shows an incorrect, incomplete, or non-standard variant
   - Review the feedback prompt text for linguistic accuracy
   - Advise on threshold sensitivity

4. **What happens with flagged clips:** If a gold standard is rejected, we select the next-best candidate from the same class (or record a fresh reference clip with the expert's guidance).

---

## Block B: Gold-Standard Validation (45 min)

### Instructions for Expert

For each of the 50 signs, play the gold-standard clip and mark:

| Rating | Meaning |
|--------|---------|
| ✅ PASS | This is a correct, complete execution of the sign |
| ⚠️ ACCEPTABLE | Minor variation but would not confuse a learner |
| ❌ REJECT | Incorrect, incomplete, or would teach bad form |

### Validation Checklist

| # | Label | Source Clip | Expert Rating | Notes |
|---|-------|-------------|---------------|-------|
| 0 | GOOD MORNING | clips/0/13.MOV | | |
| 1 | GOOD AFTERNOON | clips/1/4.MOV | | |
| 2 | GOOD EVENING | clips/2/5.MOV | | |
| 3 | HELLO | clips/3/2.MOV | | |
| 4 | HOW ARE YOU | clips/4/10.MOV | | |
| 5 | IM FINE | clips/5/13.MOV | | |
| 6 | NICE TO MEET YOU | clips/6/1.MOV | | |
| 7 | THANK YOU | clips/7/1.MOV | | |
| 8 | YOURE WELCOME | clips/8/14.MOV | | |
| 9 | SEE YOU TOMORROW | clips/9/12.MOV | | |
| 10 | UNDERSTAND | clips/10/1.MOV | | |
| 11 | DON'T UNDERSTAND | clips/11/4.MOV | | |
| 12 | KNOW | clips/12/3.MOV | | |
| 13 | DON'T KNOW | clips/13/4.MOV | | |
| 14 | NO | clips/14/0.MOV | | |
| 15 | YES | clips/15/11.MOV | | |
| 16 | WRONG | clips/16/10.MOV | | |
| 17 | CORRECT | clips/17/11.MOV | | |
| 18 | SLOW | clips/18/12.MOV | | |
| 19 | FAST | clips/19/15.MOV | | |
| 20 | ONE | clips/20/3.MOV | | |
| 21 | TWO | clips/21/13.MOV | | |
| 22 | THREE | clips/22/3.MOV | | |
| 23 | FOUR | clips/23/0.MOV | | |
| 24 | FIVE | clips/24/2.MOV | | |
| 25 | TODAY | clips/49/9.MOV | | |
| 26 | TOMORROW | clips/50/9.MOV | | |
| 27 | YESTERDAY | clips/51/10.MOV | | |
| 28 | FATHER | clips/52/4.MOV | | |
| 29 | MOTHER | clips/53/6.MOV | | |
| 30 | SON | clips/54/10.MOV | | |
| 31 | DAUGHTER | clips/55/14.MOV | | |
| 32 | GRANDFATHER | clips/56/9.MOV | | |
| 33 | GRANDMOTHER | clips/57/12.MOV | | |
| 34 | BOY | clips/62/7.MOV | | |
| 35 | GIRL | clips/63/10.MOV | | |
| 36 | MAN | clips/64/7.MOV | | |
| 37 | WOMAN | clips/65/1.MOV | | |
| 38 | DEAF | clips/66/10.MOV | | |
| 39 | HARD OF HEARING | clips/67/4.MOV | | |
| 40 | BLUE | clips/72/13.MOV | | |
| 41 | RED | clips/74/14.MOV | | |
| 42 | BLACK | clips/76/5.MOV | | |
| 43 | WHITE | clips/77/0.MOV | | |
| 44 | BREAD | clips/85/10.MOV | | |
| 45 | EGG | clips/86/18.MOV | | |
| 46 | CHICKEN | clips/89/15.MOV | | |
| 47 | RICE | clips/91/13.MOV | | |
| 48 | HOT | clips/95/13.MOV | | |
| 49 | COLD | clips/96/9.MOV | | |

### Summary After Block B

- Total PASS: ___/50
- Total ACCEPTABLE: ___/50
- Total REJECT: ___/50
- Rejected signs requiring replacement: _______________

---

## Block C: Feedback Prompt Copy Review (20 min)

### Current Prompts (from `feedback_engine.py`)

The engine produces these template-based prompts. Ask the expert to evaluate each:

#### Prompt 1: Timing
> "Your sign is {faster|slower} than the model — {take your time|keep the movement flowing}."

**Expert review:**
- [ ] Linguistically accurate for FSL context?
- [ ] "the model" → should this say "the example" or "the reference"?
- [ ] Is timing feedback useful for FSL learners? (Some signs have flexible tempo)
- Expert's suggested revision: _______________

#### Prompt 2: Motion
> "Move your {left|right} hand {left|right|higher|lower|closer to the model path}."

**Expert review:**
- [ ] Directional terms clear to a learner?
- [ ] "higher/lower" vs "up/down" — which is more natural?
- [ ] "closer to the model path" → clearer alternative?
- Expert's suggested revision: _______________

#### Prompt 3: Handshape
> "Check your {left|right}-hand shape — adjust your {finger names} finger(s)."

**Expert review:**
- [ ] Is naming specific fingers (thumb, index, etc.) helpful or confusing?
- [ ] Would showing an image/diagram be better than text? (Future enhancement)
- [ ] Are Filipino-language prompts needed for the target learner population?
- Expert's suggested revision: _______________

#### Prompt 4: Hand Not Detected
> "This sign uses your {hand} hand — keep it visible to the camera."

**Expert review:**
- [ ] Accurate for all 50 signs? (Are any one-handed signs in the set?)
- [ ] Clear enough instruction?
- Expert's suggested revision: _______________

#### Prompt 5: Orientation
> "Rotate your {hand} palm to match the model orientation."

**Expert review:**
- [ ] Is "rotate your palm" understandable without directional guidance?
- [ ] Would "face your palm {up|down|toward you|away from you}" be more actionable?
- [ ] Is orientation feedback critical for FSL or is it usually implicit in handshape?
- Expert's suggested revision: _______________

### Additional Copy Questions

6. **Mirror convention:** When the learner sees "move your right hand left," does that match their intuition while looking at a mirrored front-camera preview?
   - Expert answer: _______________

7. **Prompt volume:** If 6 feedback items fire simultaneously (worst case), should the app show only the top 3? Or all?
   - Expert answer: _______________

8. **Language:** Should prompts be in English, Filipino, or offer both?
   - Expert answer: _______________

---

## Block D: Threshold Calibration Discussion (10 min)

### Current Thresholds

| Dimension | Threshold | Triggers When |
|-----------|-----------|---------------|
| Timing | 0.30 | ~25% tempo deviation from reference |
| Motion | 0.25 | ~one hand-width positional error |
| Handshape | 0.22 | Worst finger error exceeds extended-vs-curled difference |
| Orientation | 0.25 | ~22.5° palm angle deviation |

### Questions for Expert

1. **Are these too sensitive (too many false alarms)?**
   - Which dimension, if any, triggers feedback when the sign looks "good enough"?
   - Expert answer: _______________

2. **Are these too loose (miss real errors)?**
   - The TOMORROW vs YESTERDAY demo didn't trigger motion feedback despite opposite motion direction. Is this a problem?
   - Expert answer: _______________

3. **Are all four dimensions equally important for FSL?**
   - Should handshape errors always rank higher than timing errors? Or is it sign-dependent?
   - Expert answer: _______________

4. **Per-sign threshold override:**
   - Should some signs have stricter thresholds on specific dimensions? (e.g., NUMBER signs on handshape)
   - Expert answer: _______________

---

## Block E: Sign-Off (10 min)

### Gate Closure Criteria

For Phase 10 to close, we need:

- [ ] ≥45/50 gold standards rated PASS or ACCEPTABLE (90% coverage)
- [ ] All rejected gold standards have a remediation plan (replacement clip identified or fresh recording scheduled)
- [ ] Prompt copy reviewed — critical issues addressed or accepted with documented rationale
- [ ] Expert signs off that the feedback system is "pedagogically reasonable" (not perfect, but would not actively mislead a learner)

### Expert Sign-Off

> I have reviewed the 50 gold-standard reference clips and the corrective feedback prompt copy for the Kumpas system. My assessment is:
>
> Gold standards: ___/50 approved (___PASS + ___ACCEPTABLE), ___REJECT requiring remediation.
>
> Feedback prompts: [ ] Approved as-is / [ ] Approved with noted revisions / [ ] Requires rework before deployment
>
> Overall: The feedback system [ ] IS / [ ] IS NOT pedagogically reasonable for FSL learners at this stage.
>
> Signed: _______________ Date: _______________

---

## Post-Session Actions (Author)

- [ ] Update `gold_standards_manifest.json` status field from "provisional" to "expert-approved" or "rejected"
- [ ] For rejected clips: run replacement selection or schedule recording session
- [ ] Apply prompt copy revisions to both `feedback_engine.py` (Python) and Kotlin port
- [ ] Re-run parity test after any prompt changes
- [ ] Update `docs/phase-gates.md` Phase 6 status
- [ ] Update `.kiro/specs/10-feedback-logic/design.md` §8 Open Items with expert decisions
- [ ] Commit all changes to `kiro-sdlc-framework` branch

---

## Notes Space

(Use during session for freeform expert observations)

_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
