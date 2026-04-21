@echo off
REM GitHub 仓库创建和推送脚本 (Windows)

echo ================================
echo SWHelper GitHub 仓库设置向导
echo ================================
echo.

REM 检查是否已登录 GitHub CLI
where gh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ GitHub CLI (gh) 未安装
    echo.
    echo 请安装 GitHub CLI:
    echo   Windows: winget install --id GitHub.cli
    echo   或下载: https://cli.github.com/
    echo.
    echo 或者手动创建仓库:
    echo   1. 访问 https://github.com/new
    echo   2. 创建新仓库 'SWHelper'
    echo   3. 运行: git remote add origin https://github.com/YOUR_USERNAME/SWHelper.git
    echo   4. 运行: git push -u origin master
    pause
    exit /b 1
)

REM 检查是否已登录
gh auth status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未登录 GitHub
    echo 请先登录:
    echo   gh auth login
    pause
    exit /b 1
)

echo ✅ GitHub CLI 已就绪
echo.

REM 获取仓库信息
set /p REPO_NAME="仓库名称 [SWHelper]: "
if "%REPO_NAME%"=="" set REPO_NAME=SWHelper

set /p REPO_DESC="仓库描述 [SolidWorks 2026 自动化设计系统]: "
if "%REPO_DESC%"=="" set REPO_DESC=SolidWorks 2026 自动化设计系统

set /p IS_PRIVATE="是否为私有仓库? (y/N): "
if /i "%IS_PRIVATE%"=="y" (
    set PRIVATE_FLAG=--private
) else (
    set PRIVATE_FLAG=--public
)

echo.
echo ================================
echo 准备创建 GitHub 仓库
echo ================================
echo 仓库名称: %REPO_NAME%
echo 描述: %REPO_DESC%
if "%PRIVATE_FLAG%"=="--private" (
    echo 可见性: 私有
) else (
    echo 可见性: 公开
)
echo.

set /p CONFIRM="确认创建? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo 已取消
    pause
    exit /b 0
)

REM 创建仓库
echo.
echo 正在创建 GitHub 仓库...
gh repo create "%REPO_NAME%" --description "%REPO_DESC%" %PRIVATE_FLAG% --source=. --remote=origin --push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo ✅ 仓库创建成功！
    echo ================================
    echo.
    gh repo view "%REPO_NAME%" --web
) else (
    echo.
    echo ❌ 创建失败，请手动创建
    echo.
    echo 手动步骤:
    echo   1. 访问 https://github.com/new
    echo   2. 创建仓库 '%REPO_NAME%'
    echo   3. 运行以下命令:
    echo      git remote add origin https://github.com/YOUR_USERNAME/%REPO_NAME%.git
    echo      git push -u origin master
)

pause
