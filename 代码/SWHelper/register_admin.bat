@echo off
REM 管理员注册脚本 - 注册修改后的SWHelper DLL
REM
REM 使用方法：
REM 1. 右键点击此文件
REM 2. 选择"以管理员身份运行"
REM 3. 等待注册完成

echo ========================================================================
echo SWHelper Robust - DLL 注册（需要管理员权限）
echo ========================================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] 需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [OK] 已获得管理员权限
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

echo 步骤1: 停止所有SolidWorks进程...
taskkill /F /IM SLDPWORKS.EXE 2>nul
taskkill /F /IM SLDWORKS.exe 2>nul
echo [OK] SolidWorks进程已停止
echo.

echo 步骤2: 注册SWHelper.Robust.dll...
echo.
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "bin\Release\SWHelper.Robust.dll" /codebase /tlb

if %errorLevel% equ 0 (
    echo.
    echo ========================================================================
    echo [SUCCESS] DLL注册成功！
    echo ========================================================================
    echo.
    echo 下一步：
    echo 1. 启动SolidWorks 2026
    echo 2. 运行测试: python verify_createsketch_fix.py
    echo.
) else (
    echo.
    echo ========================================================================
    echo [ERROR] DLL注册失败
    echo ========================================================================
    echo.
    echo 可能的原因：
    echo - DLL文件不存在或损坏
    echo - .NET Framework版本不匹配
    echo - 注册表权限问题
    echo.
)

pause
