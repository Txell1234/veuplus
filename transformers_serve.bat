@echo off
REM VeuPlus Transformers Service Launcher
REM Equivalent to: pip install transformers torch && transformers serve && transformers chat

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check and install dependencies
echo [1/3] Checking dependencies...
.venv\Scripts\python.exe -c "import transformers, torch; print('Dependencies OK')" 2>nul
if errorlevel 1 (
    echo Installing transformers and torch...
    .venv\Scripts\pip.exe install transformers torch
)

REM Parse command line arguments
set COMMAND=%1
set ARG1=%2
set ARG2=%3

if "%COMMAND%"=="serve" (
    echo [2/3] Starting Transformers Service...
    .venv\Scripts\python.exe transformers_serve.py serve --host 0.0.0.0 --port 8000
    goto :end
)

if "%COMMAND%"=="chat" (
    if "%ARG1%"=="" (
        echo ERROR: Server URL required
        echo Usage: transformers_serve.bat chat localhost:8000 --model-name-or-path MODEL_NAME
        goto :end
    )
    if "%ARG2%"=="" (
        echo ERROR: Model name required
        echo Usage: transformers_serve.bat chat localhost:8000 --model-name-or-path MODEL_NAME
        goto :end
    )
    echo [2/3] Starting Chat with %ARG2%...
    .venv\Scripts\python.exe transformers_serve.py chat %ARG1% --model-name-or-path %ARG2%
    goto :end
)

REM Default: show help
echo VeuPlus Transformers Service
echo.
echo Usage:
echo   transformers_serve.bat serve
echo   transformers_serve.bat chat localhost:8000 --model-name-or-path MODEL_NAME
echo.
echo Examples:
echo   transformers_serve.bat serve
echo   transformers_serve.bat chat localhost:8000 microsoft/DialoGPT-medium
echo   transformers_serve.bat chat localhost:8000 openai/gpt-oss-20b
echo.

:end
pause
