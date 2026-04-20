# Register SWHelper 100% Version
$RegAsm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
$DllPath = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Dynamic.100.dll"

Write-Host "Registering SWHelper 100% Version..."
Write-Host ""

Set-Location "D:\sw2026\代码\SWHelper"

& $RegAsm $DllPath /codebase

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Registration completed!"
    Write-Host ""
    Write-Host "Version: 1.2-100Percent-Dynamic"
    Write-Host "Methods: 16 total (10 original + 6 extended)"
    Write-Host ""
    Write-Host "New methods available:"
    Write-Host "  - CreateCut: Cut through holes for nuts"
    Write-Host "  - CreateInternalThread: Internal threads for nuts"
    Write-Host ""
    Write-Host "Ready for 100% M5 automation:"
    Write-Host "  - M5 bolt: Complete design"
    Write-Host "  - M5 nut: Complete design"
    Write-Host "  - Assembly: Thread fit verification"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Registration failed!"
    Write-Host ""
    Write-Host "Make sure to run PowerShell as Administrator!"
    Write-Host "Right-click PowerShell -^> 'Run as Administrator'"
    Write-Host ""
    exit 1
}
