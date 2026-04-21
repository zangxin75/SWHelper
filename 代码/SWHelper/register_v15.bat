@echo off
REM SWHelper V15.0 Registration Script
REM 100%% VBA Macro Automation

echo Registering SWHelper V15.0...
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator privileges required
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Change to DLL directory
cd /d "%~dp0bin\Release"

echo Step 1: Unregister old version
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister /silent

echo.
echo Step 2: Register V15.0
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo Registration SUCCESSFUL!
    echo ========================================
    echo.
    echo Version: SWHelper V15.0-VBA-Macro-Automation
    echo Feature: 100%% VBA macro automation
    echo.
    echo Next step:
    echo   cd ..\..\TestCode
    echo   python test_v15_vba_macro.py
    echo.
) else (
    echo.
    echo ========================================
    echo Registration FAILED
    echo ========================================
    echo.
    echo Please check:
    echo 1. Running as administrator
    echo 2. DLL file exists
    echo 3. .NET Framework installed
    echo.
)

pause
