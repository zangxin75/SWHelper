@echo off
echo Registering SWHelper 100%% Version...
echo.

cd /d "D:\sw2026\代码\SWHelper"

C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe bin\Release\SWHelper.Dynamic.100.dll /codebase

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Registration completed!
    echo.
    echo Version: 1.2-100Percent-Dynamic
    echo Methods: 16 total (10 original + 6 extended)
    echo.
    echo New methods available:
    echo   - CreateCut: Cut through holes for nuts
    echo   - CreateInternalThread: Internal threads for nuts
    echo.
    echo Ready for 100%% M5 automation:
    echo   - M5 bolt: Complete design
    echo   - M5 nut: Complete design
    echo   - Assembly: Thread fit verification
    echo.
) else (
    echo.
    echo [ERROR] Registration failed!
    echo.
    echo Make sure to run as Administrator!
    echo.
)

pause
