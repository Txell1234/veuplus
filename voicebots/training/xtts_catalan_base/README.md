# VeuPlus - Catalan Voice Training (XTTS v2)

This package contains everything needed to train a hyper-realistic Catalan voice for VeuPlus using XTTS v2.

## Structure

- configs/config_ca.json → Model configuration
- data/audio/ → Folder for training .wav files (22kHz, mono)
- data/metadata.csv → Transcriptions linked to audio
- models/ → Output directory for trained checkpoints
- train.sh → Script to launch training

## Requirements

- Coqui-TTS installed
- Python 3.10+
- XTTS v2 support
- Dataset: https://huggingface.co/datasets/projecte-aina/openslr-slr69-ca-trimmed-denoised

## Run training
```bash
bash train.sh
```

Once trained, integrate the model into VeuPlus using the inference API or embedding component.

## Offline dataset caching

To avoid repeated downloads, cache the Catalan datasets locally before training:

```python
from datasets import load_dataset
load_dataset("projecte-aina/openslr-slr69-ca-trimmed-denoised")
# Optionally also:
load_dataset("projecte-aina/4catac")
```

The datasets will be stored in the Hugging Face cache (respects `HF_DATASETS_CACHE`) and can be reused offline.