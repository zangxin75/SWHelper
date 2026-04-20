@echo off
echo ========================================================================
echo SWHelper Full Version - Compilation Script
echo ========================================================================
echo.

set SW_API_DIR=d:\app_install\solidworks2026\SOLIDWORKS\api\redist
set CSC_PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
set OUTPUT_DIR=bin\Release
set PROJECT_DIR=%~dp0

echo Configuration:
echo   SolidWorks API: %SW_API_DIR%
echo   C# Compiler: %CSC_PATH%
echo   Output Directory: %PROJECT_DIR%%OUTPUT_DIR%
echo.

REM Create output directory
if not exist "%PROJECT_DIR%%OUTPUT_DIR%" mkdir "%PROJECT_DIR%%OUTPUT_DIR%"

echo [1/4] Compiling SWHelper.dll...
echo.

%CSC_PATH% /target:library /out:"%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.dll" /lib:"%SW_API_DIR%" /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /reference:System.Drawing.dll /reference:System.Windows.Forms.dll /doc:"%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.xml" /nologo /warn:4 "%PROJECT_DIR%SWHelper.cs"

if %errorlevel% neq 0 (
    echo [ERROR] Compilation failed!
    echo Error code: %errorlevel%
    echo.
    echo Possible causes:
    echo   - Cannot find SolidWorks API DLLs at: %SW_API_DIR%
    echo   - Compilation errors in source code
    echo   - Missing .NET Framework
    echo.
    pause
    exit /b 1
)

echo [OK] Compilation successful!
echo.

echo [2/4] Copying SolidWorks API DLLs to output directory...
copy /Y "%SW_API_DIR%\SolidWorks.Interop.sldworks.dll" "%PROJECT_DIR%%OUTPUT_DIR%\" >nul
copy /Y "%SW_API_DIR%\SolidWorks.Interop.swconst.dll" "%PROJECT_DIR%%OUTPUT_DIR%\" >nul
echo [OK] DLLs copied
echo.

echo [3/4] Verifying output...
dir "%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.dll"
echo.

echo [4/4] Building summary:
echo   [OK] SWHelper.dll compiled successfully
echo   [OK] Located at: %PROJECT_DIR%%OUTPUT_DIR%\SWHelper.dll
echo   [OK] Ready for COM registration
echo.

echo ========================================================================
echo Compilation Complete!
echo ========================================================================
echo.

echo Next step: Register COM component
echo.
echo Run this command to register:
echo   C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.dll" /codebase
echo.

pause
