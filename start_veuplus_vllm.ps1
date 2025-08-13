$ErrorActionPreference = 'Stop'
Write-Host "== VeuPlus: inicio modo gpt-oss (vLLM) ==" -ForegroundColor Cyan

# Ir al directorio del script
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 1) Iniciar/asegurar vLLM (OpenAI-compatible) en localhost:8000
try {
  Write-Host "[vLLM] Preparando contenedor..." -ForegroundColor Yellow
  $null = & docker --version
} catch {
  Write-Error "Docker no está disponible. Instala Docker Desktop y activa GPU"; exit 1
}

try { & docker rm -f vllm_oss | Out-Null } catch {}

Write-Host "[vLLM] Iniciando openai/gpt-oss-20b en modo OpenAI API..." -ForegroundColor Yellow
& docker run --gpus all -d --name vllm_oss -p 8000:8000 vllm/vllm-openai:latest `
  --model openai/gpt-oss-20b `
  --dtype bf16 `
  --max-model-len 8192 | Out-Null

# Esperar a que responda
Write-Host "[vLLM] Esperando a que el servidor responda en http://localhost:8000 ..." -ForegroundColor Yellow
$ok = $false
for ($i=0; $i -lt 60; $i++) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing http://localhost:8000/v1/models -TimeoutSec 2
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { $ok = $true; break }
  } catch {}
  Start-Sleep -Seconds 2
}
if (-not $ok) { Write-Warning "[vLLM] No se pudo validar el arranque, continuando igualmente..." }
else { Write-Host "[vLLM] OK" -ForegroundColor Green }

# 2) Preparar backend (venv + deps mínimos)
Write-Host "[Backend] Preparando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  py -3.11 -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel | Out-Null
& .\.venv\Scripts\python.exe -m pip install fastapi==0.116.1 "uvicorn[standard]==0.35.0" transformers==4.55.0 httpx==0.27.2 numpy==2.2.6 soundfile==0.13.1 pydantic==2.11.7 python-multipart==0.0.20 | Out-Null

# 3) Exportar variables para usar vLLM
$env:TRANSFORMERS_PROVIDER = "vllm"
$env:VLLM_BASE_URL = "http://localhost:8000"
$env:TRANSFORMERS_MODEL = "openai/gpt-oss-20b"

# 4) Iniciar backend FastAPI minimizado
Write-Host "[Backend] Iniciando FastAPI en http://localhost:8001 ..." -ForegroundColor Yellow
Start-Process -WindowStyle Minimized -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn backend.server:app --host 127.0.0.1 --port 8001"

# 5) Iniciar frontend (React) minimizado
if (Test-Path .\start_frontend.bat) {
  Write-Host "[Frontend] Iniciando React en http://localhost:3000 ..." -ForegroundColor Yellow
  Start-Process -WindowStyle Minimized cmd.exe -ArgumentList "/c start_frontend.bat"
}

# 6) Abrir navegador
Start-Process msedge "http://localhost:3000"
Write-Host "== VeuPlus: modo vLLM iniciado ==" -ForegroundColor Green


