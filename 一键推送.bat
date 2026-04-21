@echo off
title SWHelper - 一键推送到 GitHub

echo ===============================================
echo   SWHelper 自动化推送工具
echo   用户: zangxin75
echo   仓库: https://github.com/zangxin75/SWHelper
echo ===============================================
echo.

cd /d D:\sw2026

echo [步骤 1/3] 检查环境...
if not exist "README.md" (
    echo ❌ 错误: 请在项目根目录运行
    pause
    exit /b 1
)
echo ✅ 项目目录正确
echo.

echo [步骤 2/3] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/zangxin75/SWHelper.git
echo ✅ 远程仓库已设置
echo.

echo [步骤 3/3] 推送代码...
echo.
echo ===============================================
echo   需要认证
echo ===============================================
echo.
echo 推送时需要输入:
echo   用户名: zangxin75
echo   密码: Personal Access Token
echo.
echo 如果还没有 Token，请先创建:
echo   1. 访问: https://github.com/settings/tokens
echo   2. 点击 "Generate new token" -^> "Generate new token (classic)"
echo   3. 名称: SWHelper Push
echo   4. 勾选: ✅ repo
echo   5. 点击 "Generate token"
echo   6. 复制 token（只显示一次！）
echo.
echo 按任意键开始推送...
pause >nul

cls
echo.
echo 正在推送，请在提示时输入凭据...
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
    echo 最可能的原因: GitHub 上还没有创建仓库
    echo.
    echo 解决方法:
    echo.
    echo [方法 1] 在 GitHub 网站创建仓库（推荐）
    echo   1. 访问: https://github.com/new
    echo   2. 仓库名: SWHelper
    echo   3. 描述: SolidWorks 2026 自动化设计系统
    echo   4. 选择 Public 或 Private
    echo   5. ⚠️ 不要勾选 "Add a README file"
    echo   6. 点击 "Create repository"
    echo   7. 重新运行此脚本
    echo.
    echo [方法 2] 使用 GitHub CLI（需要先登录）
    echo   1. 在新的 PowerShell 窗口运行: gh auth login
    echo   2. 然后: gh repo create SWHelper --public --source=. --remote=origin --push
    echo.
)

pause
