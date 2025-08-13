@echo off
echo Iniciando VeuPlus...
cd /d "%~dp0"

REM Ejecutar servidor directamente con Python del venv
echo Servidor iniciando en http://localhost:8001
.\.venv\Scripts\python.exe backend\server.py

pause
