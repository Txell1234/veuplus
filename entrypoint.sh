#!/bin/sh
set -e

# Start the FastAPI backend
cd /backend || { echo "Backend directory not found"; exit 1; }

# Optional warmups: preload XTTS model and Projecte AINA dataset
if [ "${WARMUP_TTS}" = "1" ]; then
  echo "Warming up Coqui XTTS v2 model..."
  python3 - <<'PY'
from TTS.api import TTS
try:
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    print("XTTS loaded OK")
except Exception as e:
    print("XTTS warmup failed:", e)
PY
fi

if [ "${PRELOAD_AINA_DATASET}" = "1" ]; then
  echo "Preloading Projecte AINA dataset..."
  python3 - <<'PY'
try:
    from datasets import load_dataset
    ds = load_dataset("projecte-aina/openslr-slr69-ca-trimmed-denoised", split="train[:10]", trust_remote_code=True)
    print("Aina dataset sample loaded:", len(ds))
except Exception as e:
    print("Aina dataset preload failed:", e)
PY
fi

echo "Starting FastAPI backend"
# Start Uvicorn with proper host binding
uvicorn server:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 30

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start at initialization, exiting"
    exit 1
fi

# Start Nginx
nginx -g 'daemon off;' &
NGINX_PID=$!

# Handle termination signals
trap 'kill $BACKEND_PID $NGINX_PID; exit 0' SIGTERM SIGINT

# Check if processes are still running
while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $NGINX_PID 2>/dev/null; do
    sleep 1
done

# If we get here, one of the processes died
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Nginx died, shutting down backend..."
    kill $BACKEND_PID
else
    echo "Backend died, shutting down nginx..."
    kill $NGINX_PID
fi

exit 1
