#!/bin/bash
source ../../venv/Scripts/activate
python -m TTS.bin.train_tts \
  --config_path voicebots/training/xtts_catalan_base/configs/config_ca.json \
  --out_path voicebots/training/xtts_catalan_base/models/