param([string]$PyExe)
$ErrorActionPreference = "Stop"
Write-Host "Using Python: $PyExe"
if (!(Test-Path ".\\.venv\\Scripts\\python.exe")) { & $PyExe -m venv .venv }
$venvPy = ".\\.venv\\Scripts\\python.exe"
& $venvPy -m pip install --upgrade pip setuptools wheel
& $venvPy -m pip install -r requirements.txt
