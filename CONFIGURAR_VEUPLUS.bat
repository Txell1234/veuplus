@echo off
REM Script de configuració ràpida VeuPlus per Windows
REM Configura el sistema perquè funcioni realment

echo.
echo ========================================
echo   VEUPLUS - CONFIGURACIÓ RÀPIDA
echo ========================================
echo.

REM Verificar que estem al directori correcte
if not exist "backend\server.py" (
    echo ❌ Error: Executa aquest script des del directori arrel de VeuPlus
    echo    Directori actual: %CD%
    pause
    exit /b 1
)

echo 🔍 Verificant estructura del projecte...
if not exist "config.example.env" (
    echo ❌ Error: No es troba config.example.env
    pause
    exit /b 1
)

echo ✅ Estructura del projecte correcta

REM Crear fitxer .env si no existeix
if not exist ".env" (
    echo.
    echo 📝 Creant fitxer .env...
    copy "config.example.env" ".env"
    echo ✅ Fitxer .env creat
) else (
    echo ✅ Fitxer .env ja existeix
)

echo.
echo 🔑 CONFIGURACIÓ D'API KEYS
echo ==========================
echo.
echo Per fer funcionar VeuPlus necessites configurar almenys una API key.
echo.
echo Opcions disponibles:
echo   1. OpenAI (Recomanat per començar)
echo   2. Google Gemini
echo   3. Anthropic Claude
echo   4. Saltar configuració (només per proves)
echo.

set /p choice="Selecciona una opció (1-4): "

if "%choice%"=="1" goto configure_openai
if "%choice%"=="2" goto configure_gemini
if "%choice%"=="3" goto configure_anthropic
if "%choice%"=="4" goto skip_api_config
goto invalid_choice

:configure_openai
echo.
echo 🔑 Configurant OpenAI...
echo.
echo Per obtenir una API key d'OpenAI:
echo   1. Anar a https://platform.openai.com/api-keys
echo   2. Crear nova API key
echo   3. Copiar la clau (comença per sk-)
echo.
set /p openai_key="Introdueix la teva API key d'OpenAI: "
if "%openai_key%"=="" (
    echo ❌ No s'ha introduït cap API key
    goto configure_openai
)
echo OPENAI_API_KEY=%openai_key% >> .env
echo ✅ API key d'OpenAI configurada
goto start_server

:configure_gemini
echo.
echo 🔑 Configurant Google Gemini...
echo.
echo Per obtenir una API key de Gemini:
echo   1. Anar a https://makersuite.google.com/app/apikey
echo   2. Crear nova API key
echo   3. Copiar la clau
echo.
set /p gemini_key="Introdueix la teva API key de Gemini: "
if "%gemini_key%"=="" (
    echo ❌ No s'ha introduït cap API key
    goto configure_gemini
)
echo GEMINI_API_KEY=%gemini_key% >> .env
echo ✅ API key de Gemini configurada
goto start_server

:configure_anthropic
echo.
echo 🔑 Configurant Anthropic Claude...
echo.
echo Per obtenir una API key d'Anthropic:
echo   1. Anar a https://console.anthropic.com/
echo   2. Crear nova API key
echo   3. Copiar la clau (comença per sk-ant-)
echo.
set /p anthropic_key="Introdueix la teva API key d'Anthropic: "
if "%anthropic_key%"=="" (
    echo ❌ No s'ha introduït cap API key
    goto configure_anthropic
)
echo ANTHROPIC_API_KEY=%anthropic_key% >> .env
echo ✅ API key d'Anthropic configurada
goto start_server

:skip_api_config
echo.
echo ⚠️  Saltant configuració d'API keys
echo    El sistema funcionarà amb capacitats limitades
goto start_server

:invalid_choice
echo.
echo ❌ Opció no vàlida
goto configure_openai

:start_server
echo.
echo 🚀 INICIANT SERVIDOR VEUPLUS
echo ============================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no està instal·lat o no està al PATH
    echo    Instal·la Python 3.10+ des de https://python.org
    pause
    exit /b 1
)

echo ✅ Python detectat

REM Instal·lar dependències si cal
if not exist "backend\venv" (
    echo.
    echo 📦 Creant entorn virtual...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
    echo ✅ Dependències instal·lades
) else (
    echo ✅ Entorn virtual ja existeix
)

echo.
echo 🔄 Iniciant servidor backend...
echo    Servidor disponible a: http://localhost:8080
echo    Per aturar el servidor: Ctrl+C
echo.

cd backend
call venv\Scripts\activate
python server.py

echo.
echo 🛑 Servidor aturat
pause
