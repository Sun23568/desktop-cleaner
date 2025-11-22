@echo off
REM Desktop Cleaner 打包脚本 (Windows)
REM 使用此脚本将应用打包成独立可执行文件

REM 设置 UTF-8 编码以正确显示中文
chcp 65001 >nul 2>&1

echo ========================================
echo Desktop Cleaner 打包工具
echo ========================================
echo.

REM 切换到项目根目录
cd /d "%~dp0.."

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8-3.11
    pause
    exit /b 1
)

REM 检查 Python 版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 检测到 Python 版本: %PYTHON_VERSION%

REM 提取主版本号和次版本号
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM 检查版本是否在支持范围内 (3.8-3.11)
if %MAJOR% LSS 3 (
    echo [错误] Python 版本过低，需要 Python 3.8-3.11
    echo 当前版本: %PYTHON_VERSION%
    pause
    exit /b 1
)

if %MAJOR% EQU 3 (
    if %MINOR% LSS 8 (
        echo [错误] Python 版本过低，需要 Python 3.8-3.11
        echo 当前版本: %PYTHON_VERSION%
        pause
        exit /b 1
    )
    if %MINOR% GTR 11 (
        echo [警告] Python 版本过高，PyInstaller 可能不兼容
        echo 当前版本: %PYTHON_VERSION%
        echo 推荐版本: Python 3.8-3.11
        echo.
        echo 是否继续？此操作可能失败...
        pause
    )
)

echo [1/4] 检查并安装依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo [2/4] 清理旧的构建文件...
if exist ".build_temp" rmdir /s /q .build_temp
if exist "dist" rmdir /s /q dist

echo.
echo [3/4] 开始打包应用...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller build\desktop_cleaner.spec

echo.
echo [4/4] 检查打包结果...
if exist "dist\DesktopCleaner.exe" (
    echo.
    echo ========================================
    echo 打包成功！
    echo ========================================
    echo.
    echo 可执行文件位置: dist\DesktopCleaner.exe
    echo.
    echo 你可以：
    echo 1. 直接运行 dist\DesktopCleaner.exe
    echo 2. 将 dist\DesktopCleaner.exe 复制到任何位置使用
    echo 3. 分享给其他用户（无需安装 Python）
    echo.
) else (
    echo.
    echo ========================================
    echo 打包失败！
    echo ========================================
    echo 请查看上方的错误信息
    echo.
)

pause
