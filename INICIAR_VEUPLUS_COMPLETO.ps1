# Iniciar VeuPlus Completo - Backend + Frontend
# Script per iniciar tot el sistema VeuPlus amb ALIA Kit

Write-Host "Iniciant VeuPlus Completo" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar directori
$projectRoot = "C:\Users\merit\Desktop\VeusPlus"
if (-not (Test-Path $projectRoot)) {
    Write-Host "No es troba el directori del projecte: $projectRoot" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

# 1. BACKEND
Write-Host "1. Iniciant Backend (port 8003)..." -ForegroundColor Green
Write-Host "   Directori: backend\" -ForegroundColor Gray

# Aturar processos Python anteriors
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Iniciar backend en nova finestra
$backendPath = Join-Path $projectRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'BACKEND VEUPLUS' -ForegroundColor Cyan; python server.py"

Write-Host "   Backend iniciant en nova finestra..." -ForegroundColor Green
Write-Host "   Esperant 15 segons perque el backend s'iniciï..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar backend
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method GET -TimeoutSec 5
    Write-Host "   Backend actiu: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   Backend encara iniciant o no disponible" -ForegroundColor Yellow
    Write-Host "   Esperant 10 segons mes..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

Write-Host ""

# 2. FRONTEND
Write-Host "2. Iniciant Frontend (port 3000)..." -ForegroundColor Green
Write-Host "   Directori: frontend\" -ForegroundColor Gray

# Verificar si node_modules existeix
$frontendPath = Join-Path $projectRoot "frontend"
$nodeModules = Join-Path $frontendPath "node_modules"

if (-not (Test-Path $nodeModules)) {
    Write-Host "   Instal·lant dependencies del frontend..." -ForegroundColor Yellow
    Set-Location $frontendPath
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Error instal·lant dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "   Dependencies instal·lades" -ForegroundColor Green
}

# Iniciar frontend en nova finestra
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'FRONTEND VEUPLUS' -ForegroundColor Cyan; npm run dev"

Write-Host "   Frontend iniciant en nova finestra..." -ForegroundColor Green
Write-Host "   Esperant 20 segons perque el frontend s'iniciï..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "VeuPlus Iniciat Completament" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8003" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8003/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pagines disponibles:" -ForegroundColor Yellow
Write-Host "   - Dashboard" -ForegroundColor White
Write-Host "   - ALIA Kit BSC (sense soroll!)" -ForegroundColor White
Write-Host "   - Veus Hiperreal·listes" -ForegroundColor White
Write-Host "   - Veus Edge-TTS" -ForegroundColor White
Write-Host "   - Chatbots" -ForegroundColor White
Write-Host "   - Voicebots" -ForegroundColor White
Write-Host ""
Write-Host "Consells:" -ForegroundColor Yellow
Write-Host "   - Obre http://localhost:3000 al navegador" -ForegroundColor White
Write-Host "   - Ves a 'ALIA Kit BSC' per provar veus sense soroll" -ForegroundColor White
Write-Host "   - Les finestres de backend i frontend restaran obertes" -ForegroundColor White
Write-Host ""
Write-Host "Per aturar:" -ForegroundColor Yellow
Write-Host "   - Tanca les finestres de PowerShell del backend i frontend" -ForegroundColor White
Write-Host "   - O prem Ctrl+C a cada finestra" -ForegroundColor White
Write-Host ""

# Obrir navegador automaticament
Write-Host "Obrint navegador..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Tot llest! Gaudeix de VeuPlus amb ALIA Kit!" -ForegroundColor Green
Write-Host ""
