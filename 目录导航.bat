@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo     SolidWorks AI Agent 项目 - 快速目录导航
echo ═══════════════════════════════════════════════════════════
echo.
echo 请选择要跳转的目录：
echo.
echo [1] 📄 文档目录
echo     └─ 包含研究报告、使用指南、技术文档
echo.
echo [2] 💻 代码目录
echo     └─ 包含Python脚本、VBA宏、测试代码
echo.
echo [3] 🎯 项目目录
echo     └─ MCP服务器项目
echo.
echo [4] 📦 模型文件目录
echo     └─ 包含SolidWorks零件文件
echo.
echo [5] 🗂️ 配置目录
echo     └─ 包含配置文件
echo.
echo [6] 📖 项目根目录
echo     └─ 返回项目根目录
echo.
echo [0] 🚪 退出
echo.
echo ═══════════════════════════════════════════════════════════
echo.

set /p choice=请输入选项 (0-6):

if "%choice%"=="1" (
    cd /d "%~dp0文档"
    echo.
    echo ✓ 已跳转到文档目录
    echo.
    dir /b
) else if "%choice%"=="2" (
    cd /d "%~dp0代码"
    echo.
    echo ✓ 已跳转到代码目录
    echo.
    dir /b
) else if "%choice%"=="3" (
    cd /d "%~dp0项目\SolidworksMCP-python"
    echo.
    echo ✓ 已跳转到MCP服务器项目
    echo.
    dir /b
) else if "%choice%"=="4" (
    cd /d "%~dp0模型文件"
    echo.
    echo ✓ 已跳转到模型文件目录
    echo.
    dir /b
) else if "%choice%"=="5" (
    cd /d "%~dp0配置"
    echo.
    echo ✓ 已跳转到配置目录
    echo.
    dir /b
) else if "%choice%"=="6" (
    cd /d "%~dp0"
    echo.
    echo ✓ 已返回项目根目录
    echo.
    dir /b
) else if "%choice%"=="0" (
    echo.
    echo 👋 再见！
    exit /b 0
) else (
    echo.
    echo ❌ 无效选项，请重新运行
    exit /b 1
)

echo.
cmd /k
