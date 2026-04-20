@echo off
REM Compile 100% Version with Cut and InternalThread

set SW_API_DIR=d:\app_install\solidworks2026\SOLIDWORKS\api\redist
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
set OUTPUT=bin\Release\SWHelper.Dynamic.100.dll
set SOURCE=Simple_Dynamic_Extended.cs

echo ========================================================================
echo Compiling 100%% Version - M5 Nut Complete Support
echo ========================================================================
echo.

if not exist "%SOURCE%" (
    echo ERROR: Source file not found!
    pause
    exit /b 1
)

%CSC% /target:library /out:"%OUTPUT%" /lib:"%SW_API_DIR%" /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo "%SOURCE%"

if %errorlevel% neq 0 (
    echo ERROR: Compilation failed!
    pause
    exit /b 1
)

echo.
echo [OK] Compilation successful!
echo.
echo Output: %OUTPUT%
echo.
echo New methods:
echo   [NEW] CreateCut - Cut through holes (for nuts)
echo   [NEW] CreateInternalThread - Internal threads (for nuts)
echo.
echo Total methods: 16 (10 original + 6 extended)
echo.
echo Next steps:
echo   1. Register: register.bat (as Administrator)
echo   2. Test M5 screw: python create_m5_screw.py
echo   3. Test M5 nut: python create_m5_nut_complete.py
echo.
pause
