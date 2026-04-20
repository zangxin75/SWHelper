@echo off
echo ================================================
echo 请以管理员身份运行此脚本
echo ================================================
echo.
echo 正在注册 SWHelper.Robust.dll...
echo.

cd /d "%~dp0"

REM 检查管理员权限
net session >/dev/null 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo.
    echo 请按以下步骤操作：
    echo 1. 右键点击此文件
    echo 2. 选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [OK] 已获得管理员权限
echo.

REM 执行注册
echo 正在执行注册命令...
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "bin\Release\SWHelper.Robust.dll" /codebase

echo.
if %errorLevel% equ 0 (
    echo ================================================
    echo [成功] DLL注册成功！
    echo ================================================
    echo.
    echo 现在可以测试100％自动化了：
    echo   cd D:\sw2026\代码\测试代码
    echo   py test_100_percent_automation.py
    echo.
) else (
    echo ================================================
    echo [失败] DLL注册失败
    echo ================================================
    echo.
    echo 请检查：
    echo - DLL文件是否存在
    echo - .NET Framework版本是否正确
    echo.
)

pause
