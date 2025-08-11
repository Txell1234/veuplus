# Script PowerShell para iniciar VeuPlus
Write-Host "Iniciando VeuPlus..." -ForegroundColor Green

# Cambiar al directorio correcto
Set-Location "C:\Users\merit\Desktop\VeusPlus\backend"

# Verificar que el archivo existe
if (Test-Path "server.py") {
    Write-Host "Archivo server.py encontrado" -ForegroundColor Green
} else {
    Write-Host "ERROR: server.py no encontrado" -ForegroundColor Red
    exit
}

# Verificar Python
if (Test-Path "..\\.venv\Scripts\python.exe") {
    Write-Host "Python virtual env encontrado" -ForegroundColor Green
} else {
    Write-Host "ERROR: Python virtual env no encontrado" -ForegroundColor Red
    exit
}

Write-Host "Ejecutando servidor..." -ForegroundColor Yellow
Write-Host "Una vez iniciado, ve a: http://localhost:8001" -ForegroundColor Cyan

# Ejecutar servidor
& "..\\.venv\Scripts\python.exe" "server.py"
