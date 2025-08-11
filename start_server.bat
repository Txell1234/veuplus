@echo off
echo Iniciando VeuPlus...
cd /d "%~dp0"

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Cambiar al directorio backend
cd backend

REM Ejecutar servidor
echo Servidor iniciándose en http://localhost:8001
python server.py

pause
