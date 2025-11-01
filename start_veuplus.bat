@echo ===============================================================
@echo VeuPlus - Sistema TTS Catalán Hiperrealista
@echo ===============================================================
@echo.

pushd "%~dp0"

echo Validando entorno...
if not exist "backend\server.py" (
    echo ERROR: No encontrado backend\server.py
    pause
    exit /b 1
)

echo Instalando dependencias básicas...
pip install -q fastapi uvicorn python-multipart edge-tts librosa soundfile numpy

echo.
echo Levantando servidor VeuPlus...
echo.
echo ✅ URLs disponibles:
echo    http://localhost:8002
echo    Docs API: http://localhost:8002/docs  
echo    Frontend: http://localhost:8002/ (si está construido)
echo.
echo Usar Ctrl+C para salir
echo.

set PYTHONPATH=.
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8002 --reload

popd
pause