$ErrorActionPreference = 'Stop'
Write-Host "== VeuPlus: inicio modo OpenAI ==" -ForegroundColor Cyan

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

if (-not $env:OPENAI_API_KEY) {
  Write-Error "OPENAI_API_KEY no definido. Ejecuta: `$env:OPENAI_API_KEY = 'sk-...'"; exit 1
}

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  py -3.11 -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel | Out-Null
& .\.venv\Scripts\python.exe -m pip install fastapi==0.116.1 "uvicorn[standard]==0.35.0" transformers==4.55.0 httpx==0.27.2 numpy==2.2.6 soundfile==0.13.1 pydantic==2.11.7 openai==1.99.6 python-multipart==0.0.20 | Out-Null

Write-Host "[Backend] Iniciando FastAPI en http://localhost:8001 ..." -ForegroundColor Yellow
Start-Process -WindowStyle Minimized -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn backend.server:app --host 127.0.0.1 --port 8001"

if (Test-Path .\start_frontend.bat) {
  Write-Host "[Frontend] Iniciando React en http://localhost:3000 ..." -ForegroundColor Yellow
  Start-Process -WindowStyle Minimized cmd.exe -ArgumentList "/c start_frontend.bat"
}

Start-Process msedge "http://localhost:3000"
Write-Host "== VeuPlus: modo OpenAI iniciado ==" -ForegroundColor Green


