$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

$env:DEVELOPMENT_MODE = "true"
$env:TRANSFORMERS_PROVIDER = "local"
$env:TRANSFORMERS_MODEL = "distilgpt2"
$env:TRANSFORMERS_LOAD_IN_4BIT = "0"
$env:DISABLE_TRANSFORMERS_INIT = "0"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"

Write-Host "Starting VeuPlus API on http://localhost:8010 ..."
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8010 --reload

