@echo off
REM Simple registration script - pure ASCII
echo ============================================================
echo Register SWHelper.Robust V6
echo ============================================================
echo.

REM Check admin rights
net session >/dev/null 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator rights required
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

cd /d "%~dp0bin\Release"

echo Current directory: %CD%
echo.

echo Step 1: Unregister old version...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister 2>/dev/null
echo.

echo Step 2: Register new version...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase
if errorlevel 1 (
    echo.
    echo ERROR: Registration failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Registration complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Close all SolidWorks instances
echo   2. Close all PowerShell windows
echo   3. Start SolidWorks 2026
echo   4. Run: py test_createpart_v6_nocache.py
echo.
pause
