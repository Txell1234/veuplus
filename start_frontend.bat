@echo off
echo Iniciando Frontend...
cd /d "%~dp0"

REM Resolver ruta de npm (soporta instalaciones comunes)
set "NPM=%ProgramFiles%\nodejs\npm.cmd"
if not exist "%NPM%" set "NPM=%ProgramFiles(x86)%\nodejs\npm.cmd"
if not exist "%NPM%" set "NPM=%LOCALAPPDATA%\Programs\nodejs\npm.cmd"

if not exist "%NPM%" (
    echo ERROR: npm no encontrado. Instala Node.js LTS y vuelve a intentarlo.
    pause
    exit /b 1
)

REM Cambiar al directorio frontend
cd frontend

REM Instalar dependencias si es necesario
if not exist node_modules (
    echo Instalando dependencias...
    call "%NPM%" install
)

REM Ejecutar frontend
echo Frontend iniciandose en http://localhost:3000
call "%NPM%" start

pause
