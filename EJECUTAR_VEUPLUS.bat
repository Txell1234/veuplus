@echo off
title VeuPlus - Plataforma de Voz Catalana
color 0A

echo ========================================
echo     VEUPLUS - PLATAFORMA DE VOZ CATALANA
echo ========================================
echo.

cd /d "%~dp0"

REM 1. Verificar entorno virtual
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado
    echo.
    echo Para solucionarlo, ejecuta:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [1/5] Activando entorno virtual...
call .venv\Scripts\activate.bat

REM 2. Verificar dependencias del backend
echo [2/5] Verificando dependencias del backend...
.venv\Scripts\python.exe -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo      Instalando dependencias...
    .venv\Scripts\pip.exe install -q -r requirements.txt
)

REM 3. Construir frontend si no existe
echo [3/5] Verificando frontend...
if not exist "frontend\build" (
    if exist "frontend\package.json" (
        echo      Construyendo frontend...
        cd frontend
        if not exist node_modules npm install --silent
        npm run build --silent
        cd ..
    )
)

REM 4. Iniciar servidor
echo [4/5] Iniciando servidor VeuPlus...
cd backend
echo.
echo ========================================
echo   SERVIDOR VEUPLUS INICIADO
echo ========================================
echo.
echo 🌐 Interfaz Web: http://localhost:8001
echo 📖 API Docs:     http://localhost:8001/docs  
echo ❤️  Health:      http://localhost:8001/api/health
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

..\\.venv\Scripts\python.exe server.py
