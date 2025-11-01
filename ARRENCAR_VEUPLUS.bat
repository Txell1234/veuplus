@echo off
title VeuPlus - Iniciar Backend i Frontend
color 0A

echo ========================================
echo     VEUPLUS - ARRENCAR PROJECTE
echo ========================================
echo.

cd /d "%~dp0"

REM Iniciar Backend en terminal separada
echo [1/2] Iniciant Backend...
start "VeuPlus Backend" cmd /k "cd /d C:\Users\merit\Desktop\VeusPlus\backend && python server.py"

REM Esperar 2 segons
timeout /t 2 /nobreak > nul

REM Iniciar Frontend en terminal separada
echo [2/2] Iniciant Frontend...
start "VeuPlus Frontend" cmd /k "cd /d C:\Users\merit\Desktop\VeusPlus\frontend && npm run dev"

echo.
echo ========================================
echo   PROJECTE ARRENCAT!
echo ========================================
echo.
echo   Backend:  http://localhost:8080
echo   Frontend: http://localhost:3000
echo.
echo   Tanca aquesta finestra quan vulguis
echo ========================================

pause


