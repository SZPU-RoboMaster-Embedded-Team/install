@echo off
REM Windows 一键安装工具启动脚本
REM 检查 Python 是否安装

REM 切换到脚本所在目录
cd /d %~dp0

echo ===============================================================================
echo       欢迎使用 Windows 一键安装工具
echo ===============================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.6 或更高版本
    echo.
    echo 你可以通过以下方式安装 Python:
    echo   1. 访问 https://www.python.org/downloads/ 下载安装
    echo   2. 使用 winget 安装: winget install Python.Python.3
    echo.
    pause
    exit /b 1
)

echo [信息] 检测到 Python 已安装
python --version
echo.

echo [信息] 正在启动一键安装工具...
echo.

python install.py

echo.
echo ===============================================================================
echo       感谢使用 Windows 一键安装工具
echo ===============================================================================
pause
