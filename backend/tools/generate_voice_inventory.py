#!/usr/bin/env python3
"""
Utility to inventory local hyperrealistic voice assets.

Scans:
 - backend/training_data/*         (metadata, processed.wav, etc.)
 - backend/voice_models/*          (model checkpoints, samples)

Outputs:
 - backend/voice_inventory.json    with consolidated metadata
 - prints a short table to stdout
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.hyperrealistic_engine import build_inventory
OUTPUT_PATH = ROOT / "backend" / "voice_inventory.json"


def main() -> int:
    inventory = build_inventory()
    OUTPUT_PATH.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Inventory written to {OUTPUT_PATH}")
    print("\nHyperrealistic voices:")
    for item in inventory["voices"]:
        status = f"{item.get('source')} | mock={item.get('mock')}"
        print(f" - {item['id']}: {status}")

    print("\nVoice model files:")
    for item in inventory["voice_model_files"]:
        print(f" - {item['name']}: {len(item.get('files', []))} files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
