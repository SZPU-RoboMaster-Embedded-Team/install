@echo off
REM UTF-8 version - ensure file is saved as UTF-8 encoding
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ===============================================================================
echo       Windows Installation Tool
echo ===============================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python 3.6 or higher
    echo.
    echo You can install Python by:
    echo   1. Visit https://www.python.org/downloads/
    echo   2. Use winget: winget install -e --id Python.Python.3.11
    echo.
    pause
    exit /b 1
)

echo [INFO] Python detected
python --version
echo.

echo [INFO] Starting installation tool...
echo.

python install.py

echo.
echo ===============================================================================
echo       Thank you for using Windows Installation Tool
echo ===============================================================================
pause
