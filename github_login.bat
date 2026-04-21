@echo off
REM GitHub CLI 登录和推送脚本

echo ================================
echo GitHub CLI - 登录和推送
echo ================================
echo.

REM 刷新环境变量
call refreshenv 2>nul

REM 检查gh是否可用
where gh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI 已安装，但需要刷新环境变量
    echo.
    echo 请关闭此窗口，打开新的 PowerShell 或命令提示符，然后运行:
    echo   github_login.bat
    echo.
    pause
    exit /b 1
)

echo ✅ GitHub CLI 已就绪
echo.

REM 检查是否已登录
gh auth status >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ 已登录到 GitHub
    echo.
    gh auth status
    echo.
    echo 准备创建仓库并推送...
    echo.
    goto :create_repo
)

echo =================================
echo 步骤 1: 登录到 GitHub
echo =================================
echo.
echo 按照提示完成登录:
echo   1. 按 Enter 选择默认选项 (GitHub.com)
echo   2. 选择 HTTPS
echo   3. 选择 Yes (登录)
echo   4. 按提示在浏览器中授权
echo.

pause

gh auth login

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 登录失败
    pause
    exit /b 1
)

echo.
echo ✅ 登录成功！
echo.

:create_repo
echo =================================
echo 步骤 2: 创建仓库并推送
echo =================================
echo.

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
echo 准备创建:
echo   名称: %REPO_NAME%
echo   描述: %REPO_DESC%
echo   可见性: %PRIVATE_FLAG%
echo.

set /p CONFIRM="确认创建? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo 正在创建 GitHub 仓库并推送...
echo.

gh repo create "%REPO_NAME%" --description "%REPO_DESC%" %PRIVATE_FLAG% --source=. --remote=origin --push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo ✅ 成功！
    echo ================================
    echo.
    gh repo view "%REPO_NAME%" --web
) else (
    echo.
    echo ❌ 创建失败
    echo.
    echo 请检查:
    echo   1. 仓库名是否已被占用
    echo   2. 网络连接是否正常
    echo   3. 是否有足够的权限
)

echo.
pause
