@echo off
REM ============================================================
REM Switch to Extended Version
REM ============================================================

echo.
echo ========================================================================
echo Switch to SWHelper Extended Version
echo ========================================================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Administrator privileges required!
    echo.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [OK] Administrator privileges obtained
echo.

set DLL_DIR=D:\sw2026\代码\SWHelper\bin\Release
set BASE_DLL=%DLL_DIR%\SWHelper.Dynamic.dll
set EXTENDED_DLL=%DLL_DIR%\SWHelper.Dynamic.Extended.dll
set REGASM=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe

REM Step 1: Unregister base version
echo ========================================================================
echo Step 1/3: Unregister Base Version
echo ========================================================================
echo.

echo Unregistering: %BASE_DLL%
"%REGASM%" "%BASE_DLL%" /u >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Base version unregistered
) else (
    echo [INFO] Base version was not registered or already unregistered
)

echo.

REM Step 2: Register extended version
echo ========================================================================
echo Step 2/3: Register Extended Version
echo ========================================================================
echo.

echo Registering: %EXTENDED_DLL%
"%REGASM%" "%EXTENDED_DLL%" /codebase

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Registration failed!
    pause
    exit /b 1
)

echo.
echo [OK] Extended version registered
echo.

REM Step 3: Verify registration
echo ========================================================================
echo Step 3/3: Verify Registration
echo ========================================================================
echo.

echo Checking registry...
reg query "HKCR\SWHelper.SWHelperDynamic\CLSID" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] COM class registered
) else (
    echo [WARNING] COM class not found in registry
)

echo.
echo ========================================================================
echo Switch Complete!
echo ========================================================================
echo.
echo Current Version: Extended (v1.1)
echo New Methods Available:
echo   [NEW] DrawCircle - Draw circles
echo   [NEW] DrawLine - Draw lines
echo   [NEW] CreateRevolution - Revolution features
echo   [NEW] CreateFillet - Fillet features
echo   [NEW] CreateChamfer - Chamfer features
echo.
echo Next steps:
echo   1. Run test: python D:\sw2026\代码\测试代码\test_extended_features.py
echo   2. Design M5 screw: python D:\sw2026\代码\测试代码\create_m5_screw.py
echo.
pause
