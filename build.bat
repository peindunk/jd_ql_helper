@echo off
chcp 65001 >nul
echo ===== JD Cookie 助手打包工具 =====
echo.

REM 检查是否安装了 PyInstaller
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo PyInstaller 安装失败，请手动安装后重试。
        exit /b 1
    )
)

echo 开始打包应用程序...
echo.

REM 清理旧的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM 检查图标文件是否存在
set "icon_path=assets\app_icon.ico"
if not exist "%icon_path%" (
    echo 警告: 图标文件 "%icon_path%" 不存在，将使用默认图标
    set "icon_param="
) else (
    set "icon_param=--icon=%icon_path%"
)

REM 使用 PyInstaller 打包
python -m PyInstaller ^
    --name=JDCookieHelper ^
    --windowed ^
    --onefile ^
    %icon_param% ^
    --clean ^
    --noconfirm ^
    --add-data="assets;assets" ^
    --add-data="about;about" ^
    --add-data="database;database" ^
    --add-data="core;core" ^
    main.py

if %errorlevel% neq 0 (
    echo 打包失败！
    exit /b 1
)

echo.
echo 打包完成！可执行文件位于: dist\JDCookieHelper.exe