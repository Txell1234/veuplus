# Iniciar VeuPlus amb 3 Sistemes Diferenciats

Write-Host "================================" -ForegroundColor Cyan
Write-Host "VEUPLUS - 3 SISTEMES TTS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# PAS 1: Verificar Edge-TTS
Write-Host "1. Verificant Edge-TTS..." -ForegroundColor Green

try {
    python -c "import edge_tts; print('Edge-TTS OK')" 2>$null
    Write-Host "   Edge-TTS instal·lat" -ForegroundColor Green
} catch {
    Write-Host "   Instal·lant Edge-TTS..." -ForegroundColor Yellow
    pip install edge-tts
    Write-Host "   Edge-TTS instal·lat" -ForegroundColor Green
}

Write-Host ""

# PAS 2: Aturar processos anteriors
Write-Host "2. Netejant processos anteriors..." -ForegroundColor Green
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "   Processos netejats" -ForegroundColor Green

Write-Host ""

# PAS 3: Iniciar Backend
Write-Host "3. Iniciant Backend..." -ForegroundColor Green
$backendPath = "C:\Users\merit\Desktop\VeusPlus\backend"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'BACKEND - 3 SISTEMES TTS' -ForegroundColor Cyan; python server.py"

Write-Host "   Backend iniciant..." -ForegroundColor Green
Write-Host "   Esperant 15 segons..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar backend
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method GET -TimeoutSec 5
    Write-Host "   Backend actiu!" -ForegroundColor Green
} catch {
    Write-Host "   Backend encara iniciant..." -ForegroundColor Yellow
}

Write-Host ""

# PAS 4: Iniciar Frontend
Write-Host "4. Iniciant Frontend..." -ForegroundColor Green
$frontendPath = "C:\Users\merit\Desktop\VeusPlus\frontend"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'FRONTEND - 3 SISTEMES TTS' -ForegroundColor Cyan; npm run dev"

Write-Host "   Frontend iniciant..." -ForegroundColor Green
Write-Host "   Esperant 20 segons..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "SISTEMES INICIATS" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8003" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8003/docs" -ForegroundColor Cyan
Write-Host ""

Write-Host "3 SISTEMES DISPONIBLES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. SISTEMA 1 - Edge-TTS Standard" -ForegroundColor White
Write-Host "      Pagina: /edge-tts-standard" -ForegroundColor Gray
Write-Host "      Endpoint: /api/edge-tts/*" -ForegroundColor Gray
Write-Host "      Veus: ~400 idiomes globals" -ForegroundColor Gray
Write-Host "      SEGRE: No" -ForegroundColor Gray
Write-Host ""

Write-Host "   2. SISTEMA 2 - Catala Edge+SEGRE" -ForegroundColor White
Write-Host "      Pagina: /catalan-hyperrealistic" -ForegroundColor Gray
Write-Host "      Endpoint: /api/catalan/*" -ForegroundColor Gray
Write-Host "      Veus: Enric, Joana (catalanes)" -ForegroundColor Gray
Write-Host "      SEGRE: Si (pronunciacio optimitzada)" -ForegroundColor Gray
Write-Host ""

Write-Host "   3. SISTEMA 3 - ALIA BSC Premium" -ForegroundColor White
Write-Host "      Pagina: /alia-kit-bsc" -ForegroundColor Gray
Write-Host "      Endpoint: /api/alia/*" -ForegroundColor Gray
Write-Host "      Veus: Alba, Alvaro, Ainhoa, Sabela" -ForegroundColor Gray
Write-Host "      SEGRE: Si (nomes catala)" -ForegroundColor Gray
Write-Host "      Idiomes: ca, es, eu, gl" -ForegroundColor Gray
Write-Host ""

Write-Host "PROVA-HO:" -ForegroundColor Yellow
Write-Host "   1. Obre: http://localhost:3000" -ForegroundColor White
Write-Host "   2. Prova cada sistema amb el mateix text" -ForegroundColor White
Write-Host "   3. Escolta les diferencies!" -ForegroundColor White
Write-Host ""

# Obrir navegador
Write-Host "Obrint navegador..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Tot llest! Els 3 sistemes estan actius!" -ForegroundColor Green
Write-Host ""

