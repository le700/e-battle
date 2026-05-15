@echo off
setlocal

echo ================================
echo FriendBattle - Windows 打包脚本
echo ================================
echo.

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo 步骤 1: 检查环境...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装
    pause
    exit /b 1
)

pip list | findstr /i pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

echo ✅ 环境检查完成

echo.
echo 步骤 2: 创建必要目录...
if not exist assets mkdir assets
if not exist build mkdir build
if not exist dist mkdir dist

echo ✅ 目录创建完成

echo.
echo 步骤 3: 打包为 EXE...

pyinstaller pyinstaller.spec --clean

echo.
echo ✅ 打包完成！
echo.
echo 输出位置: %PROJECT_DIR%dist\FriendBattle.exe
echo.
echo 使用方法:
echo   1. 运行 dist\FriendBattle.exe
echo   2. 访问 http://localhost:3000
echo   3. 开始你的 FriendBattle！
echo.

pause
