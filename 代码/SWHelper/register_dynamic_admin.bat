@echo off
REM ============================================================
REM Register SWHelper.Dynamic.dll - Elevated
REM This script will request Administrator privileges
REM ============================================================

echo.
echo ========================================================================
echo Register SWHelper Dynamic Version - Administrator Request
echo ========================================================================
echo.

REM Check if already running as administrator
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Already running as administrator
    echo.
    echo Launching PowerShell registration script...
    echo.
    PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0register_dynamic_elevated.ps1"
    pause
    exit /b 0
)

echo [INFO] Requesting Administrator privileges...
echo.

REM Create a temporary PowerShell script to elevate
echo PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0register_dynamic_elevated.ps1\"' -Verb RunAs" > "%~dp0temp_elevate.ps1"

REM Run the elevation script
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0temp_elevate.ps1"

REM Clean up
del "%~dp0temp_elevate.ps1" >nul 2>&1

exit /b 0
