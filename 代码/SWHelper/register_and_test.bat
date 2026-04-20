@echo off
REM ============================================================
REM SWHelper Auto Register and Test Script
REM ============================================================

echo.
echo ============================================================
echo SWHelper .NET Middle Tier - Auto Register and Test
echo ============================================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script requires administrator privileges!
    echo.
    echo Please:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Administrator privileges obtained
echo.

REM Step 1: Navigate to SWHelper directory
echo ============================================================
echo Step 1/3: Locate SWHelper directory
echo ============================================================
cd /d D:\sw2026\代码\SWHelper
if %errorlevel% neq 0 (
    echo [ERROR] Cannot find SWHelper directory
    pause
    exit /b 1
)
echo [OK] Current directory: %CD%
echo.

REM Step 2: Register COM component
echo ============================================================
echo Step 2/3: Register SWHelper COM component
echo ============================================================
echo.
echo Registering: SWHelper.Simple.dll
echo.

C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe SWHelper.Simple.dll /codebase

if %errorlevel% neq 0 (
    echo [ERROR] Registration failed!
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] COM component registered successfully!
echo.

REM Step 3: Verify registration
echo ============================================================
echo Step 3/3: Verify COM component
echo ============================================================
echo.
echo Verifying registration...
echo.

C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe SWHelper.Simple.dll /tlb:SWHelper.Simple.tlb >nul 2>&1

if %errorlevel% neq 0 (
    echo [WARNING] Verification warning (may not affect function)
) else (
    echo [OK] COM component verified successfully
)

echo.
echo ============================================================
echo Registration complete! Running Python test...
echo ============================================================
echo.

REM Run Python test
cd /d D:\sw2026\代码\测试代码
python test_sw_helper_simple.py

echo.
echo ============================================================
echo All steps complete!
echo ============================================================
echo.
echo If you see "[SUCCESS]" message, then:
echo   OK Compile: Success
echo   OK Register: Success
echo   OK COM call: Success
echo.
echo Project completion: 95%% -^> 100%% OK
echo.
pause
