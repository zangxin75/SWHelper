# Register Fixed Version
$RegAsm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
$DllPath = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Dynamic.Fixed.dll"

Write-Host "Registering Fixed Version..."
Write-Host ""

Set-Location "D:\sw2026\代码\SWHelper"

& $RegAsm $DllPath /codebase

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Registration completed!"
    Write-Host ""
    Write-Host "Version: 1.2-Fixed-Dynamic"
    Write-Host "Fix: CreatePart using default template"
    Write-Host ""
    Write-Host "Ready to test M5 design!"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Registration failed!"
    Write-Host ""
    Write-Host "Make sure to run PowerShell as Administrator!"
    exit 1
}
