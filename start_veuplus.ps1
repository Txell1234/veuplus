# Script principal para iniciar VeusPlus completo
Write-Host ""
Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         VeusPlus - Inicio Completo       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚡ Características:" -ForegroundColor Yellow
Write-Host "   • Voces Catalanas Hiperrealistas (con grabaciones reales)" -ForegroundColor White
Write-Host "   • Voces Edge-TTS Multiidioma (Microsoft Neural)" -ForegroundColor White
Write-Host "   • Chatbots y Voicebots con IA" -ForegroundColor White
Write-Host ""

# Verificar requisitos
Write-Host "🔍 Verificando requisitos..." -ForegroundColor Cyan

$pythonOk = $false
$nodeOk = $false

try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    $pythonOk = $true
} catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
}

try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    $nodeOk = $true
} catch {
    Write-Host "❌ Node.js no encontrado" -ForegroundColor Red
}

Write-Host ""

if (-not $pythonOk -or -not $nodeOk) {
    Write-Host "❌ Faltan requisitos. Instala:" -ForegroundColor Red
    if (-not $pythonOk) { Write-Host "   • Python 3.8+ desde https://www.python.org" -ForegroundColor Yellow }
    if (-not $nodeOk) { Write-Host "   • Node.js 18+ desde https://nodejs.org" -ForegroundColor Yellow }
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "📋 Para iniciar VeusPlus, abre DOS ventanas de PowerShell:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Ventana 1 (Backend):" -ForegroundColor White
Write-Host "   .\start_backend.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "   Ventana 2 (Frontend):" -ForegroundColor White
Write-Host "   .\start_frontend.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "💡 O usa el archivo start_veuplus_auto.ps1 para inicio automático" -ForegroundColor Yellow
Write-Host ""

$respuesta = Read-Host "¿Quieres iniciar el backend ahora? (S/N)"
if ($respuesta -eq "S" -or $respuesta -eq "s") {
    Write-Host ""
    Write-Host "🚀 Iniciando backend..." -ForegroundColor Green
    Write-Host "   Abre otra PowerShell y ejecuta: .\start_frontend.ps1" -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
    & "$PSScriptRoot\start_backend.ps1"
}