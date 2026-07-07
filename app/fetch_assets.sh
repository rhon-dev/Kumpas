#!/usr/bin/env bash
# Fetch binary assets the app needs but the repo doesn't track
# (.task and .tflite are gitignored). Run once after cloning.
set -euo pipefail
cd "$(dirname "$0")"
ASSETS=android/app/src/main/assets
mkdir -p "$ASSETS"

curl -sL -o "$ASSETS/pose_landmarker_lite.task" \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
curl -sL -o "$ASSETS/hand_landmarker.task" \
  https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task

# classifier + labels come from the training pipeline (kumpas-data lives next to the repo)
cp ../../kumpas-data/tflite/kumpas_50sign_builtins_dynamic.tflite "$ASSETS/kumpas_50sign.tflite"
cp ../../kumpas-data/sequences/label_map.json "$ASSETS/label_map.json"

ls -la "$ASSETS"
