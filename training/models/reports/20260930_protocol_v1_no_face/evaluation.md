# Exploratory evaluation — 20260930_153819_protocol_v1_no_face_baseline

**Status: exploratory, NOT a pristine final test.** The existing FSL-105 test split was consulted in historical model experiments. This run was selected using validation only, but the test clips are not newly unseen to the project.

**Scope:** Accuracy on the specified FSL-105 clip split; signer-independent generalization not established (no verified signer IDs).

- Correct: 181/203
- Accuracy: 0.8916
- Macro F1: 0.8852
- Clip-level Wilson 95% interval: [0.8414, 0.9273]; assumes independent clips, which is not verified without signer identities.

| Class | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| GOOD MORNING | 4 | 1.000 | 1.000 | 1.000 |
| GOOD AFTERNOON | 4 | 1.000 | 1.000 | 1.000 |
| GOOD EVENING | 5 | 1.000 | 1.000 | 1.000 |
| HELLO | 4 | 0.800 | 1.000 | 0.889 |
| HOW ARE YOU | 4 | 1.000 | 1.000 | 1.000 |
| IM FINE | 4 | 1.000 | 1.000 | 1.000 |
| NICE TO MEET YOU | 5 | 1.000 | 1.000 | 1.000 |
| THANK YOU | 4 | 1.000 | 1.000 | 1.000 |
| YOURE WELCOME | 4 | 1.000 | 0.750 | 0.857 |
| SEE YOU TOMORROW | 4 | 1.000 | 1.000 | 1.000 |
| UNDERSTAND | 4 | 1.000 | 0.750 | 0.857 |
| DON’T UNDERSTAND | 4 | 1.000 | 1.000 | 1.000 |
| KNOW | 4 | 1.000 | 1.000 | 1.000 |
| DON’T KNOW | 4 | 1.000 | 0.750 | 0.857 |
| NO | 4 | 0.400 | 0.500 | 0.444 |
| YES | 4 | 0.500 | 0.250 | 0.333 |
| WRONG | 4 | 1.000 | 0.750 | 0.857 |
| CORRECT | 5 | 0.833 | 1.000 | 0.909 |
| SLOW | 4 | 1.000 | 1.000 | 1.000 |
| FAST | 4 | 0.750 | 0.750 | 0.750 |
| ONE | 4 | 1.000 | 1.000 | 1.000 |
| TWO | 4 | 0.571 | 1.000 | 0.727 |
| THREE | 4 | 0.500 | 0.250 | 0.333 |
| FOUR | 4 | 0.667 | 0.500 | 0.571 |
| FIVE | 4 | 0.500 | 0.500 | 0.500 |
| TODAY | 4 | 1.000 | 1.000 | 1.000 |
| TOMORROW | 4 | 0.667 | 1.000 | 0.800 |
| YESTERDAY | 4 | 1.000 | 0.500 | 0.667 |
| FATHER | 4 | 1.000 | 1.000 | 1.000 |
| MOTHER | 4 | 1.000 | 1.000 | 1.000 |
| SON | 4 | 1.000 | 1.000 | 1.000 |
| DAUGHTER | 4 | 1.000 | 1.000 | 1.000 |
| GRANDFATHER | 4 | 1.000 | 0.750 | 0.857 |
| GRANDMOTHER | 4 | 1.000 | 1.000 | 1.000 |
| BOY | 4 | 1.000 | 1.000 | 1.000 |
| GIRL | 4 | 0.750 | 0.750 | 0.750 |
| MAN | 4 | 0.800 | 1.000 | 0.889 |
| WOMAN | 4 | 1.000 | 1.000 | 1.000 |
| DEAF | 4 | 1.000 | 1.000 | 1.000 |
| HARD OF HEARING | 4 | 0.800 | 1.000 | 0.889 |
| BLUE | 4 | 0.800 | 1.000 | 0.889 |
| RED | 4 | 0.800 | 1.000 | 0.889 |
| BLACK | 4 | 0.800 | 1.000 | 0.889 |
| WHITE | 4 | 1.000 | 1.000 | 1.000 |
| BREAD | 4 | 1.000 | 1.000 | 1.000 |
| EGG | 4 | 1.000 | 1.000 | 1.000 |
| CHICKEN | 4 | 1.000 | 0.750 | 0.857 |
| RICE | 4 | 1.000 | 1.000 | 1.000 |
| HOT | 4 | 1.000 | 1.000 | 1.000 |
| COLD | 4 | 1.000 | 1.000 | 1.000 |
