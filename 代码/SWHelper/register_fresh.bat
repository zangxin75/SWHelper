@echo off
echo Registering SWHelper.Robust (Fresh Installation)...
cd /d "%~dp0bin\Release"
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase /tlb:SWHelper.Robust.tlb
echo.
echo Registration complete!
echo.
echo Verification:
reg query HKCR\SWHelper.Robust /ve
reg query HKCR\SWHelper.Robust\CLSID /ve
echo.
echo Press any key to exit...
pause
