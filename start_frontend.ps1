# Script para iniciar el frontend de VeusPlus
Write-Host "🚀 Iniciando Frontend VeusPlus..." -ForegroundColor Cyan

# Verificar Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no encontrado. Por favor instala Node.js 18+" -ForegroundColor Red
    exit 1
}

# Ir al directorio frontend
Set-Location -Path "$PSScriptRoot\frontend"

# Verificar si existen node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias de npm..." -ForegroundColor Yellow
    npm install
}

# Iniciar servidor de desarrollo
Write-Host ""
Write-Host "✅ Iniciando servidor frontend..." -ForegroundColor Green
Write-Host "🌐 La URL se mostrará a continuación" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

npm run dev













