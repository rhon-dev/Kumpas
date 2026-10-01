# Signer identity and evaluation scope — FSL-105

Date: 2026-09-29. Protocol: `docs/superpowers/specs/2026-09-29-evaluation-protocol-design.md`.

## What can be checked

- The locally supplied `train.csv` and `test.csv` each contain only `vid_path,id_label,label,category`. There is no signer or participant ID column.
- Parsing numeric video filename stems across all 105 classes yields 22 distinct indices (0–21) in the original train CSV, 22 in the test CSV, and an intersection of all 22. These stems are **clip indices, not verified identities**; their overlap neither proves nor disproves person overlap. Selected 50-class source clip paths remain disjoint.
- The public dataset record describes the clips and their split but does not supply a per-clip signer map. A search of the creator's dataset record and thesis/paper summaries did not establish a signer-disjoint split. The dataset authors or a documented, privacy-respecting manual review of source clips would be needed for affirmative signer identity evidence. Do not treat body-geometry clusters as ground-truth IDs.

## Defensible statement

“Accuracy on the specified FSL-105 clip split; signer-independent generalization not established.” The historic 193/203 (95.07%) score is **exploratory**, because four previously logged model runs consulted that test split. The historic validation set also held augmented versions of fit clips, so its maximum 1.0 accuracy is not independent validation. New protocol runs select on original-clip-held-out validation but still evaluate on the previously inspected 203 test clips; the reported test therefore stays exploratory even when the new code no longer selects by it.

If an authoritative clip-to-signer mapping becomes available, freeze it and create a separate, versioned signer-disjoint protocol. Do not revise these historical results in place.

## Retrieval checked

- Dataset creator's Mendeley record: `https://data.mendeley.com/datasets/48y2y99mb9/2` (description of 2,130 clips and CSV split; no signer mapping in metadata supplied locally).
- Creator's FSL105 paper: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4476867` and associated thesis `https://animorepository.dlsu.edu.ph/etdm_ece/25` (public summaries found; no authoritative per-clip signer IDs extracted). These searches are not proof that signer identities do not exist in private project records.
