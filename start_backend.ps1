# Script para iniciar el backend de VeusPlus
Write-Host "🚀 Iniciando Backend VeusPlus..." -ForegroundColor Cyan

# Verificar Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.8+" -ForegroundColor Red
    exit 1
}

# Ir al directorio backend
Set-Location -Path "$PSScriptRoot\backend"

# Verificar si existe venv
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Activar venv
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Instalar dependencias si es necesario
if (-not (Test-Path "venv\Lib\site-packages\fastapi")) {
    Write-Host "📥 Instalando dependencias..." -ForegroundColor Yellow
    pip install -r ..\requirements.txt
}

# Iniciar servidor
Write-Host ""
Write-Host "✅ Iniciando servidor backend en http://localhost:8001" -ForegroundColor Green
Write-Host "📚 Documentación API: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001













