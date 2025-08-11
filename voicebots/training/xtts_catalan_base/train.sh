#!/usr/bin/env bash
set -euo pipefail

# Cross-platform guidance:
# - Linux/macOS: ensure Python 3 and Coqui-TTS are installed in your environment
# - Windows: use WSL or Git Bash; activate your venv before calling this script

PYTHON=${PYTHON:-python3}
CONFIG_PATH=${CONFIG_PATH:-voicebots/training/xtts_catalan_base/configs/config_ca.json}
OUT_PATH=${OUT_PATH:-voicebots/training/xtts_catalan_base/models/}

echo "Starting XTTS v2 training..."
echo "Python: $($PYTHON --version)"

$PYTHON -m TTS.bin.train_tts \
  --config_path "$CONFIG_PATH" \
  --out_path "$OUT_PATH"