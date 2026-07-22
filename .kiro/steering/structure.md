# Repo Structure Conventions — Kumpas

## Directory Layout

```
kumpas/
├── .kiro/
│   ├── steering/          # Always-included context for AI agents
│   │   ├── product.md     # Problem, users, thesis framing, novelty
│   │   ├── tech.md        # Stack, architecture, build commands
│   │   └── structure.md   # This file — repo layout conventions
│   └── specs/             # Spec-driven phases (requirements.md, design.md, tasks.md)
│       ├── 00-project-init/
│       ├── 01-project-brief/
│       ├── ...
│       └── 20-defense-and-maintenance/
├── docs/
│   ├── PRD.md             # Original governance doc (historical reference)
│   ├── phase-gates.md     # Live status tracker
│   ├── dataset-notes.md   # FSL-105 findings and implications
│   └── design/            # Figma export PNGs
├── training/              # Python pipeline (Data + Model + Export agents)
│   ├── preprocessing/     # Audit, landmark extraction, sequence building
│   ├── augmentation/      # Augmentation scripts + logs
│   ├── models/            # CNN-LSTM training, experiment logs, eval reports
│   ├── feedback/          # Gold-standard builder, feedback engine reference impl
│   ├── tflite_export/     # Export scripts + logs
│   └── notebooks/         # Colab notebooks
├── app/                   # Flutter project (Mobile agent)
│   └── lib/
│       ├── camera/        # Camera pipeline
│       ├── inference/     # TFLite runtime integration
│       ├── feedback_engine/ # Kotlin/Dart port of feedback logic
│       └── ui/            # Screens and widgets
├── benchmarking/          # QA harnesses + results (independent from model agent)
├── evaluation/            # Pre/post study stats scripts
├── AGENTS.md              # Short agent context (loaded first by AI agents)
└── README.md              # Project overview
```

## Conventions

- **Dataset location:** Always outside the repo at `../FSL-105 A dataset for recognizing 105 Filipino sign language videos/`. Referenced via `--dataset-dir` CLI args.
- **Model artifacts:** Checkpoints and .tflite files live in `training/models/` and `training/tflite_export/` respectively. Large binaries (>50MB) go in .gitignore.
- **Experiment logs:** Every training run appends to `training/models/experiments_log.json`. Never silently overwrite previous results.
- **Augmentation logs:** Every augmentation run produces a log file with seed, transforms applied, and sample counts.
- **Benchmark results:** Logged in `benchmarking/` in a comparable format across iterations for thesis plotting.
- **Spec phases:** Each spec folder gets `requirements.md` and `design.md` during planning. `tasks.md` is added only once that spec's design is approved and implementation begins.
- **No network calls in app code:** Enforced by architecture, verified by privacy checklist.
- **No raw video in repo:** .gitignore blocks .MOV, .mp4, .zip containing video data.

## File Naming

- Python: snake_case for files and functions
- Dart/Flutter: snake_case for files, camelCase for variables/functions, PascalCase for classes
- Specs: kebab-case folder names with numeric prefix (e.g., `04-data-pipeline/`)
- Reports: date-prefixed where applicable (e.g., `20260705_194813_no_face_eval.md`)
