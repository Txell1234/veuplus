@echo off
echo Instalando dependencias faltantes...
cd /d "%~dp0"
..\.venv\Scripts\pip.exe install librosa soundfile datasets torch torchaudio numpy TTS unsloth unsloth_zoo
echo Dependencias instaladas. Iniciando servidor...
..\.venv\Scripts\python.exe server.py
pause
