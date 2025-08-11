@echo off
echo ========================================
echo         INICIANDO VEUPLUS
echo ========================================

cd /d "%~dp0"

REM Verificar que existe el entorno virtual
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: No se encuentra el entorno virtual
    echo Por favor, ejecuta primero: python -m venv .venv
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/4] Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Verificar dependencias básicas
echo [2/4] Verificando dependencias...
.venv\Scripts\python.exe -c "import fastapi, uvicorn; print('Backend OK')" 2>nul
if errorlevel 1 (
    echo Instalando dependencias del backend...
    .venv\Scripts\pip.exe install -r requirements.txt
)

REM Iniciar backend en background
echo [3/4] Iniciando backend en puerto 8001...
cd backend
start "VeuPlus Backend" /MIN ..\\.venv\Scripts\python.exe server.py
cd ..

REM Esperar un poco para que el backend arranque
timeout /t 3 /nobreak >nul

REM Verificar que el backend responde
echo [4/4] Verificando backend...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 5 | Out-Null; Write-Host 'Backend OK' } catch { Write-Host 'Backend no responde' }"

echo ========================================
echo   VEUPLUS INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Backend: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo Health: http://localhost:8001/api/health
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul

REM Cerrar procesos al salir
taskkill /F /FI "WINDOWTITLE eq VeuPlus Backend" 2>nul
