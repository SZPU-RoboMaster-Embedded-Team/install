@echo off
setlocal EnableExtensions

REM Build script for packaging install.py into dist\install.exe
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set "DIST_DIR=dist"
set "BUILD_DIR=build"
set "WORK_DIR=%BUILD_DIR%\work"
set "SPEC_DIR=%BUILD_DIR%\spec"

echo ===============================================================================
echo       Build EXE with PyInstaller
echo ===============================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH. Please install Python 3.6+ first.
    pause
    exit /b 1
)

echo [INFO] Python detected:
python --version
echo.

echo [INFO] Checking PyInstaller...
python -m pip show pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] PyInstaller not found, installing...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

echo [INFO] Cleaning previous build artifacts...
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%SPEC_DIR%\install.spec" del /f /q "%SPEC_DIR%\install.spec"
if exist "install.spec" del /f /q "install.spec"

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%SPEC_DIR%" mkdir "%SPEC_DIR%"

echo [INFO] Packaging...
python -m PyInstaller --noconfirm --clean --onefile --name install --collect-submodules tools --distpath "%DIST_DIR%" --workpath "%WORK_DIR%" --specpath "%SPEC_DIR%" install.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Packaging failed.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Packaging completed.
echo [INFO] Output: %cd%\%DIST_DIR%\install.exe
echo [INFO] Spec:   %cd%\%SPEC_DIR%\install.spec
echo ===============================================================================
pause
exit /b 0
