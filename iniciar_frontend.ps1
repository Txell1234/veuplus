# Iniciar Frontend VeuPlus
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Iniciant Frontend VeuPlus" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Write-Host "`nNavegant a directori frontend..." -ForegroundColor Yellow
Set-Location -Path "frontend"

Write-Host "`nInstal·lant dependències (si cal)..." -ForegroundColor Yellow
npm install

Write-Host "`nIniciant servidor de desenvolupament..." -ForegroundColor Green
Write-Host "El frontend s'obrirà a: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nPresiona Ctrl+C per aturar el frontend" -ForegroundColor Yellow
Write-Host "============================================`n" -ForegroundColor Cyan

npm run dev

