@echo off
REM Switch to Extended Version
REM Run as Administrator

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

REM Check files
if not exist "%EXTENDED_DLL%" (
    echo ERROR: Extended DLL not found!
    echo Location: %EXTENDED_DLL%
    echo.
    echo Please run compile_extended.bat first
    pause
    exit /b 1
)

echo [OK] Extended DLL found
echo.

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
    echo [INFO] Base version was not registered
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
    echo Error code: %errorlevel%
    pause
    exit /b 1
)

echo.
echo [OK] Extended version registered
echo.

REM Step 3: Verify
echo ========================================================================
echo Step 3/3: Verify Registration
echo ========================================================================
echo.

reg query "HKCR\SWHelper.SWHelperDynamic" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] COM class registered
) else (
    echo [WARNING] COM class not found
)

echo.
echo ========================================================================
echo Switch Complete!
echo ========================================================================
echo.
echo Version: Extended (v1.1)
echo New Features:
echo   [NEW] DrawCircle
echo   [NEW] DrawLine
echo   [NEW] DrawPolygon (if implemented)
echo   [NEW] CreateRevolution
echo   [NEW] CreateFillet
echo   [NEW] CreateChamfer
echo.
echo Next Steps:
echo   1. Verify: python D:\sw2026\代码\测试代码\quick_verify.py
echo   2. Test: python D:\sw2026\代码\测试代码\create_m5_screw.py
echo.
pause
