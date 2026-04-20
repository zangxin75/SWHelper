@echo off
echo ========================================================================
echo SWHelper Full Version Compilation
echo ========================================================================
echo.

set MSBUILD="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
set PROJECT="D:\sw2026\代码\SWHelper\SWHelper.csproj"

echo Using MSBuild: %MSBUILD%
echo Project: %PROJECT%
echo.

echo [1/2] Cleaning previous build...
%MSBUILD% %PROJECT% /t:Clean /p:Configuration=Release /v:minimal

echo.
echo [2/2] Building SWHelper.dll...
%MSBUILD% %PROJECT% /t:Build /p:Configuration=Release /v:normal

if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    echo Error code: %errorlevel%
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo Build Complete!
echo ========================================================================
echo.

echo Output location: D:\sw2026\代码\SWHelper\bin\Release\SWHelper.dll
echo.

pause
