#!/usr/bin/env python
"""
Placeholder de entrenamiento real para Coqui XTTS.

Uso (ejemplo):
  python scripts/train_coqui_xtts.py --manifest backend/preprocessed_data/<job_id>/audio/manifest.csv \
         --out backend/models/<job_id> --epochs 50 --batch-size 4 --lr 1e-4

Salida esperada (para que el pipeline parsee progreso): líneas con 'epoch=X/Y loss=Z'.

Nota: Este script no descarga datasets ni se distribuye con modelos. Respeta licencias
de los datasets (p. ej. Projecte AINA) accediendo a ellos vía Hugging Face en tu entorno.
"""
import argparse
import os
import time
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-4)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Simulación de entrenamiento real. Sustituir por llamada a Coqui/XTTS.
    total = max(1, args.epochs)
    for epoch in range(1, total + 1):
        # Simular tiempo de epoch
        time.sleep(0.5)
        loss = max(0.05, 2.0 - (epoch / total) * 1.9)
        print(f"epoch={epoch}/{total} loss={loss:.4f}", flush=True)

    # Guardar un marcador de finalización
    (out_dir / "trainer_done.txt").write_text("ok", encoding="utf-8")


if __name__ == "__main__":
    main()


