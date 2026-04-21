@echo off
REM 推送到 GitHub - zangxin75/SWHelper

echo ================================
echo 推送到 GitHub
echo 用户: zangxin75
echo 仓库: SWHelper
echo ================================
echo.

REM 刷新环境变量
set "PATH=%PATH%;C:\Program Files\GitHub CLI;C:\Users\zhy\AppData\Local\GitHub CLI"

REM 检查gh命令
where gh >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 正在刷新环境变量...
    call setx PATH "%PATH%" >nul 2>nul
    set "PATH=%PATH%;C:\Program Files\GitHub CLI;C:\Users\zhy\AppData\Local\GitHub CLI;C:\Program Files\Git\cmd"
    echo.
)

echo 步骤 1: 检查登录状态...
gh auth status >nul 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未登录到 GitHub
    echo.
    echo ============================================
    echo 步骤 1.5: 登录到 GitHub
    echo ============================================
    echo.
    echo 按照提示操作:
    echo   1. 选择 GitHub.com (按 Enter)
    echo   2. 选择 HTTPS (按 Enter)
    echo   3. 选择 Yes 登录 (按 Enter)
    echo   4. 复制浏览器中的授权码并粘贴
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
)

echo ✅ 已登录到 GitHub
echo.

echo ============================================
echo 步骤 2: 创建仓库并推送
echo ============================================
echo.
echo 仓库信息:
echo   URL: https://github.com/zangxin75/SWHelper
echo   名称: SWHelper
echo   描述: SolidWorks 2026 自动化设计系统
echo.

set /p IS_PRIVATE="创建为私有仓库? (y/N): "
if /i "%IS_PRIVATE%"=="y" (
    set PRIVATE_FLAG=--private
    echo   可见性: 私有
) else (
    set PRIVATE_FLAG=--public
    echo   可见性: 公开
)

echo.
set /p CONFIRM="确认创建并推送? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo 正在创建仓库并推送，请稍候...
echo.

gh repo create SWHelper --description "SolidWorks 2026 自动化设计系统" %PRIVATE_FLAG% --source=. --remote=origin --push

if %ERRORLEVEL% EQU 0 (
    cls
    echo.
    echo ================================
    echo ✅ 成功推送到 GitHub！
    echo ================================
    echo.
    echo 仓库地址:
    echo   https://github.com/zangxin75/SWHelper
    echo.
    echo 正在打开浏览器...
    echo.
    start https://github.com/zangxin75/SWHelper

    echo.
    echo ============================================
    echo 仓库内容检查
    echo ============================================
    echo.
    gh repo view SWHelper --json name,url,description,owner --jq '"仓库: \(.name)\nURL: \(.url)\n所有者: \(.owner.login)\n描述: \(.description)"'

    echo.
    echo 按任意键查看详细信息...
    pause >nul

    gh repo view SWHelper --web
) else (
    echo.
    echo ❌ 推送失败
    echo.
    echo 可能的原因:
    echo   1. 仓库名 "SWHelper" 已存在
    echo   2. 网络连接问题
    echo   3. 权限不足
    echo.
    echo 解决方法:
    echo   如果仓库已存在，使用以下命令推送:
    echo.
    echo   git remote add origin https://github.com/zangxin75/SWHelper.git
    echo   git push -u origin master
    echo.
)

pause
