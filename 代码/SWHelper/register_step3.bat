@echo off
echo ================================================
echo SWHelper.Robust.dll Registration
echo ================================================
echo.

cd /d "%~dp0"

echo Registering COM component...
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "bin\Release\SWHelper.Robust.dll" /codebase

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Registration completed!
    echo.
    echo You can now test the automation:
    echo   cd D:\sw2026\代码\测试代码
    echo   py test_100_percent_automation.py
) else (
    echo.
    echo [ERROR] Registration failed!
    echo   Please run as Administrator
)

echo.
pause
