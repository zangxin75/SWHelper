@echo off
title SWHelper - SSH 推送到 GitHub

chcp 65001 >nul
cls

echo ===============================================
echo   SWHelper SSH 推送工具
echo   用户: zangxin75
echo   认证: SSH 密钥
echo ===============================================
echo.

cd /d D:\sw2020 2>nul || cd /d D:\sw2026

if not exist "README.md" (
    echo ❌ 错误: 请在项目根目录运行
    pause
    exit /b 1
)

echo ✅ 在项目根目录
echo.

echo ===============================================
echo   步骤 1/3: 检查 SSH 密钥
echo ===============================================
echo.

if exist "%USERPROFILE%\.ssh\id_ed25519.pub" (
    echo ✅ SSH 密钥已存在
    echo.
    echo 公钥内容:
    echo.
    type "%USERPROFILE%\.ssh\id_ed25519.pub"
    echo.
) else (
    echo ❌ 未找到 SSH 密钥
    echo.
    echo 正在生成 SSH 密钥...
    echo.

    ssh-keygen -t ed25519 -C "zangxin75@github" -f "%USERPROFILE%\.ssh\id_ed25519" -N ""

    if %ERRORLEVEL% NEQ 0 (
        echo ❌ 生成密钥失败
        echo.
        echo 请安装 Git for Windows:
        echo   https://git-scm.com/download/win
        pause
        exit /b 1
    )

    echo ✅ SSH 密钥生成成功
    echo.
    echo 公钥内容:
    echo.
    type "%USERPROFILE%\.ssh\id_ed25519.pub"
    echo.
)

echo ===============================================
echo   步骤 2/3: 添加密钥到 GitHub
echo ===============================================
echo.
echo 请按以下步骤添加 SSH 密钥:
echo.
echo   1. 访问: https://github.com/settings/ssh/new
echo   2. Title: SWHelper-PC
echo   3. Key: 复制上面的公钥（整行）
echo   4. 点击 "Add SSH key"
echo.

set /p READY="完成后按 Enter 继续..."
echo.

echo ===============================================
echo   步骤 3/3: 测试并推送
echo ===============================================
echo.

echo 正在配置远程仓库...
git remote remove origin 2>nul
git remote add origin git@github.com:zangxin75/SWHelper.git
echo ✅ 远程仓库已配置 (SSH)
echo.

echo 正在测试 SSH 连接...
ssh -T git@github.com 2>&1 | findstr /C:"successfully authenticated" >nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ SSH 连接成功
    echo.
) else (
    echo ⚠️  SSH 连接可能失败
    echo.
    echo 首次连接会提示 "Are you sure you want to continue connecting?"
    echo 请输入: yes
    echo.
    echo 测试连接:
    ssh -T git@github.com
    echo.
)

set /p CONFIRM="确认推送? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo 已取消
    pause
    exit /b 0
)

cls
echo.
echo 正在推送代码到 GitHub...
echo.

git push -u origin master

if %ERRORLEVEL% EQU 0 (
    cls
    echo.
    echo ===============================================
    echo   ✅ 推送成功！
    echo ===============================================
    echo.
    echo 仓库地址:
    echo   https://github.com/zangxin75/SWHelper
    echo.
    echo SSH URL:
    echo   git@github.com:zangxin75/SWHelper.git
    echo.
    echo 正在打开浏览器...
    start https://github.com/zangxin75/SWHelper
    echo.
) else (
    cls
    echo.
    echo ===============================================
    echo   ❌ 推送失败
    echo ===============================================
    echo.
    echo 可能的原因:
    echo   1. SSH 密钥未添加到 GitHub
    echo   2. GitHub 仓库未创建
    echo   3. 网络连接问题
    echo.
    echo 解决方法:
    echo.
    echo 方法1 - 添加 SSH 密钥:
    echo   访问: https://github.com/settings/ssh/new
    echo   粘贴公钥: type "%USERPROFILE%\.ssh\id_ed25519.pub"
    echo.
    echo 方法2 - 在 GitHub 创建仓库:
    echo   访问: https://github.com/new
    echo   仓库名: SWHelper
    echo   ⚠️  不要勾选 "Add a README file"
    echo.
    echo 方法3 - 测试 SSH 连接:
    echo   ssh -T git@github.com
    echo.
)

pause
