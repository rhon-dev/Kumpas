# C1 host07 task brief

Approved host-only Package C release tooling slice. Only new inspect_release.py and test_inspect_release.py source files are owned here. Preserve app, build configuration, training, B2, protected files and prior evidence. No builds, devices, installations or commits.

Current Gradle uses standard Android src/main/assets, Flutter source ../.. and tasks-vision 0.10.14 / LiteRT 1.1.2 dependencies. Current asset directory contains gold_standards.bin, hand_landmarker.task, kumpas_50sign.tflite, label_map.json and pose_landmarker_lite.task. Discovery's historical inspection uses assets/kumpas_50sign.tflite. Existing ZIP directory confirms all five under assets/. Historical release has ARM64 Flutter libraries but also other-ABI dependency libraries: do not equate Flutter ABI set with complete native ABI set.

Implement stdlib explicit-file CLI with strict versioned independent expectation, required checkout asset bindings, protected hashes and exact ABI/native file lists. Reject ambiguous ZIP names and duplicate entries. Output is optional, confined under explicit output-root, exclusive and byte-readback verified. Errors are fixed codes; JSON rejects duplicate keys and nonfinite constants. Tests use tiny synthetic public CLI fixtures; retain meaningful behavioral RED and GREEN per slice. Report existing APKs as historical, current hashes as checkout capture only, never build/signature/runtime attestation.

Read PRD, phase gates, approved host design/plan Package C, tooling discovery, current Gradle/assets and B2 bounded acceptance. Baseline has 82 protected originals. Parent performs independent review and final-phase fresh builds.
