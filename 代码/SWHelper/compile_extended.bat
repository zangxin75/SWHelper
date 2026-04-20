@echo off
REM ============================================================
REM SWHelper Extended Version - Compilation Script
REM ============================================================

set SW_API_DIR=d:\app_install\solidworks2026\SOLIDWORKS\api\redist
set CSC_PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
set OUTPUT_DIR=bin\Release
set PROJECT_DIR=%~dp0
set SOURCE=Simple_Dynamic_Extended.cs
set OUTPUT_DLL=SWHelper.Dynamic.Extended.dll

echo ========================================================================
echo SWHelper Extended Version - Compilation
echo ========================================================================
echo.
echo Configuration:
echo   SolidWorks API: %SW_API_DIR%
echo   C# Compiler: %CSC_PATH%
echo   Source: %SOURCE%
echo   Output: %OUTPUT_DLL%
echo.

REM Verify source file
if not exist "%PROJECT_DIR%%SOURCE%" (
    echo [ERROR] Source file not found: %SOURCE%
    pause
    exit /b 1
)

echo [OK] Source file found: %SOURCE%
echo.

REM Backup original DLL
if exist "%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.Dynamic.dll" (
    echo Backing up original DLL...
    copy "%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.Dynamic.dll" "%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.Dynamic.backup" >nul
    echo [OK] Backup created
    echo.
)

REM Compile extended version
echo ========================================================================
echo Compiling Extended Version...
echo ========================================================================
echo.

%CSC_PATH% /target:library /out:"%PROJECT_DIR%%OUTPUT_DIR%\%OUTPUT_DLL%" /lib:"%SW_API_DIR%" /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo /warn:4 "%PROJECT_DIR%%SOURCE%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Compilation failed!
    echo Error code: %errorlevel%
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Compilation successful!
echo.

REM Copy DLLs
echo ========================================================================
echo Copying Files...
echo ========================================================================
echo.

copy /Y "%SW_API_DIR%\SolidWorks.Interop.sldworks.dll" "%PROJECT_DIR%%OUTPUT_DIR%\" >nul
copy /Y "%SW_API_DIR%\SolidWorks.Interop.swconst.dll" "%PROJECT_DIR%%OUTPUT_DIR%\" >nul

echo [OK] DLLs copied
echo.

REM Show output
echo ========================================================================
echo Compilation Complete!
echo ========================================================================
echo.

echo Output: %PROJECT_DIR%%OUTPUT_DIR%\%OUTPUT_DLL%
echo.

dir "%PROJECT_DIR%%OUTPUT_DIR%\%OUTPUT_DLL%"
echo.

echo ========================================================================
echo New Features Added:
echo ========================================================================
echo.
echo   [NEW] DrawCircle - Draw circles (for cylinders)
echo   [NEW] DrawLine - Draw lines
echo   [NEW] CreateRevolution - Revolution features (for cylinders, spheres)
echo   [NEW] CreateFillet - Fillet features
echo   [NEW] CreateChamfer - Chamfer features
echo.

echo Total Methods: 14 (10 original + 4 extended + 1 version update)
echo.

echo ========================================================================
echo Next Steps:
echo ========================================================================
echo.
echo 1. Unregister old version (if registered):
echo    C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "%PROJECT_DIR%%OUTPUT_DIR%\SWHelper.Dynamic.dll" /u
echo.
echo 2. Register new version:
echo    C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe "%PROJECT_DIR%%OUTPUT_DIR%\%OUTPUT_DLL%" /codebase
echo.
echo 3. Test new features:
echo    python test_extended_features.py
echo.
pause
