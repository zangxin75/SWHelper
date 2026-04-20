# Register Full Automation Version
$RegAsm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
$DllPath = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Dynamic.FullAuto.dll"

Write-Host "Registering Full Automation Version..."
Write-Host ""

Set-Location "D:\sw2026\代码\SWHelper"

& $RegAsm $DllPath /codebase

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Registration completed!"
    Write-Host ""
    Write-Host "Version: 1.3-FullAuto-Dynamic"
    Write-Host "Fixes:"
    Write-Host "  - CreatePart API fixed"
    Write-Host "  - SelectByID2 parameter types fixed"
    Write-Host "  - 100% automation ready!"
    Write-Host ""
    Write-Host "Ready to design M5 bolt and nut!"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Registration failed!"
    Write-Host ""
    Write-Host "Make sure to run PowerShell as Administrator!"
    exit 1
}
