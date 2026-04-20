@echo off
setlocal enabledelayedexpansion

set "SW_API=d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
set "CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
set "OUT=bin\Release\SWHelper.Dynamic.100.dll"
set "SRC=Simple_Dynamic_Extended.cs"
set "CURDIR=%~dp0"

echo Compiling 100%% version...
echo.

pushd "%CURDIR%"

"%CSC%" /target:library /out:"%OUT%" /lib:"%SW_API%" /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo "%SRC%"

popd

if errorlevel 1 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)

echo.
echo SUCCESS! Compiled: %OUT%
echo.
echo New methods added:
echo   CreateCut - Cut through holes
echo   CreateInternalThread - Internal threads
echo.
echo Next: register.bat (as Administrator)
echo.
pause
