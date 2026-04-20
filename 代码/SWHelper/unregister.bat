@echo off
echo Unregistering SWHelper.Robust...
cd /d "%~dp0bin\Release"
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister
echo Unregister complete.
pause
