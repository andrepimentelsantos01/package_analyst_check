@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if /I not "%~1"=="--local" (
    echo Uso: .\start --local
    exit /b 2
)

python -c "import pandas, numpy" >nul 2>&1
if errorlevel 1 (
    echo Dependências não encontradas.
    echo Execute: pip install -r requirements.txt
    exit /b 1
)

python -m examples.basic_usage
