@echo off
echo Iniciando VeuPlus...
cd /d "%~dp0"

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Ir al backend
cd backend

REM Ejecutar servidor
echo Servidor iniciando en http://localhost:8001
python server.py

pause
