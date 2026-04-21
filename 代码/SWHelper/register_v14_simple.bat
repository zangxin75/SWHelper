@echo off
REM SWHelper V14.0 Registration Script
REM Version: 14.0-VBA-Integration

echo Registering SWHelper V14.0...
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

echo Step 1: Unregister old version (if exists)
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister /silent

echo.
echo Step 2: Register new version
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo Registration SUCCESSFUL!
    echo ========================================
    echo.
    echo Version: SWHelper V14.0-VBA-Integration
    echo Feature: CreateSketch uses VBA verified method
    echo.
    echo Next step: Run test
    echo   cd ..\..\TestCode
    echo   python test_v14_vba_integration.py
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
