@echo off
echo ============================================================
echo Register SWHelper.Robust V6 - Final Version (22:39)
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

echo DLL information:
dir SWHelper.Robust.dll | findstr "SWHelper.Robust.dll"
echo.

echo Step 1: Unregister old version...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister 2>/dev/null
echo Done.

echo.
echo Step 2: Register new version...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase
if errorlevel 1 (
    echo.
    echo ERROR: Registration failed
    pause
    exit /b 1
)
echo Done.

echo.
echo ============================================================
echo Registration complete!
echo ============================================================
echo.
echo IMPORTANT: Close all applications before testing:
echo   - Close all SolidWorks instances
echo   - Close all PowerShell windows
echo.
echo Then run: py test_createpart_v6_nocache.py
echo.
pause
