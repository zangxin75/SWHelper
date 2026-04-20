@echo off
echo ============================================================
echo 重新注册 SWHelper.Robust V6 版本
echo ============================================================
echo.

cd /d "%~dp0bin\Release"

echo 步骤1: 卸载旧版本
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister 2>nul

echo.
echo 步骤2: 注册新版本
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase /tlb:SWHelper.Robust.tlb

if errorlevel 1 (
    echo.
    echo [ERROR] Registration failed
    echo Please run as Administrator
    pause
    exit /b 1
)

echo.
echo ============================================================
echo V6 版本注册完成！
echo ============================================================
echo.
echo Changes in V6:
echo   - Fixed CreatePart to use full template path
echo   - Template: C:\ProgramData\SolidWorks\SolidWorks 2026\templates\gb_part.prtdot
echo.
echo Next steps:
echo   1. Close all SolidWorks instances
echo   2. Close all PowerShell windows
echo   3. Start SolidWorks 2026
echo   4. Run test: py test_createpart_v6.py
echo.
pause
