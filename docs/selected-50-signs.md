# Approved 50-Sign Subset

Selected 2026-07-05 per team instruction ("research most used everyday signs, pick 50").
Machine-readable list: `training/preprocessing/selected_classes.json` (pipeline scripts consume that file — edit both together if the list changes).
Individual signs can still be swapped by the FSL Expert before Phase 2 training starts; swaps after training require re-training.

## Selection basis

Beginner/everyday FSL curricula and guides consistently prioritize greetings, polite and survival expressions, family terms, numbers, colors, food/drink, and time words:

- [Benilde SDEAS — FSL Learning Program](https://sdeas.benilde.edu.ph/fsllp/) (essential vocabulary for everyday conversations)
- [Kakamay Movement — Basic Sign Language](https://kakamaymovement.com/basic-sign-language)
- [Deaf Association of Quezon Province — FSL](https://daqp.org/fsl/)
- [Inquirer — Basic phrases to get started on learning FSL](https://newsinfo.inquirer.net/1168598/basic-phrases-to-get-started-on-learning-filipino-sign-language)
- [PageOne — 10 Basic FSL signs you can use every day](https://pageone.ph/10-basic-filipino-sign-language-that-you-can-use-everyday/)

Month and weekday names were excluded: low everyday frequency for a beginner practice app, and as initialized/abbreviation signs they are mutually confusable — bad for both pedagogy and classifier margins.

## The 50 signs

| Category | Kept | IDs | Notes |
|---|---|---|---|
| GREETING | 10/10 | 0–9 | Whole category — core of every beginner curriculum |
| SURVIVAL | 10/10 | 10–19 | Whole category — yes/no/understand/correct etc., highest practical value |
| NUMBER | 5/10 | 20–24 | ONE–FIVE. SIX–TEN dropped: similar handshapes → confusion risk, lower priority |
| DAYS | 3/10 | 49–51 | TODAY, TOMORROW, YESTERDAY. Weekday names dropped |
| FAMILY | 6/10 | 52–57 | FATHER, MOTHER, SON, DAUGHTER, GRANDFATHER, GRANDMOTHER. PARENTS dropped (compound of FATHER+MOTHER — overlaps both classes) |
| RELATIONSHIPS | 6/10 | 62–67 | BOY, GIRL, MAN, WOMAN, DEAF, HARD OF HEARING — identity signs essential for this app's context |
| COLOR | 4/13 | 72, 74, 76, 77 | BLUE, RED, BLACK, WHITE — basic color-term hierarchy |
| FOOD | 4/10 | 85, 86, 89, 91 | BREAD, EGG, CHICKEN, RICE — Filipino staples |
| DRINK | 2/10 | 95, 96 | HOT, COLD — highest-frequency words in the category |

**Excluded (55):** all 12 months, 7 weekday names, SIX–TEN, UNCLE, AUNTIE, COUSIN, PARENTS, WHEELCHAIR PERSON, BLIND, DEAF BLIND, MARRIED, 9 colors (GREEN, BROWN, YELLOW, ORANGE, GRAY, PINK, VIOLET, LIGHT, DARK), 6 foods (FISH, MEAT, SPAGHETTI, LONGANISA, SHRIMP, CRAB), 8 drinks (JUICE, MILK, COFFEE, TEA, BEER, WINE, SUGAR, NO SUGAR).

Sample counts per class (~20 clips each, ~16/4 train/test) are in `training/preprocessing/audit_report.json`.
