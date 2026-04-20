@echo off
setlocal enabledelayedexpansion

echo ========================================================================
echo SWHelper COM Component - Detailed Registration Script
echo ========================================================================
echo.

REM Check admin rights
echo [1/5] Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo.
    echo Please run this script as administrator:
    echo   1. Right-click on Command Prompt
    echo   2. Select "Run as administrator"
    echo   3. Navigate to this directory
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)
echo [OK] Administrator privileges confirmed
echo.

REM Navigate to directory
echo [2/5] Navigating to SWHelper directory...
cd /d D:\sw2026\代码\SWHelper
if not exist SWHelper.Simple.dll (
    echo [ERROR] SWHelper.Simple.dll not found!
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)
echo [OK] Found SWHelper.Simple.dll
echo   Size:
dir SWHelper.Simple.dll | find "SWHelper.Simple.dll"
echo.

REM Display registration command
echo [3/5] Registration command:
echo.
echo   Command: C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe SWHelper.Simple.dll /codebase
echo.

REM Execute registration
echo [4/5] Executing registration...
echo.
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe SWHelper.Simple.dll /codebase
if %errorlevel% neq 0 (
    echo [ERROR] Registration failed with error code: %errorlevel%
    echo.
    echo Possible causes:
    echo   - DLL is corrupted
    echo   - .NET Framework version mismatch
    echo   - Missing dependencies
    echo.
    pause
    exit /b 1
)
echo [OK] Registration command executed
echo.

REM Verify registration
echo [5/5] Verifying registration...
echo.
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe SWHelper.Simple.dll /tlb:SWHelper.Simple.tlb
if %errorlevel% neq 0 (
    echo [WARNING] Type library export failed (may not affect functionality)
) else (
    echo [OK] Type library exported successfully
)

echo.
echo ========================================================================
echo Registration Summary
echo ========================================================================
echo.
echo Check the output above for:
echo   [OK]   - Successful operations
echo   [ERROR] - Failed operations
echo.
echo Expected success messages:
echo   "类型已成功导出"
echo   "程序集已成功注册"
echo.

echo Next step: Run Python test
echo.
echo Press any key to run Python test...
pause >nul

echo.
echo ========================================================================
echo Running Python Test
echo ========================================================================
echo.
cd /d D:\sw2026\代码\测试代码

echo Running: python test_sw_helper_simple.py
echo.
python test_sw_helper_simple.py

echo.
echo ========================================================================
echo Complete!
echo ========================================================================
echo.
pause
