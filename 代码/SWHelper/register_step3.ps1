# SWHelper.Robust.dll Registration Script
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "SWHelper.Robust.dll - COM Component Registration" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check for Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as Administrator and execute:" -ForegroundColor Yellow
    Write-Host "  cd D:\sw2026\代码\SWHelper" -ForegroundColor Yellow
    Write-Host "  .\register_step3.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Registering SWHelper.Robust.dll..." -ForegroundColor Cyan
Write-Host ""

$regasmPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
$dllPath = "bin\Release\SWHelper.Robust.dll"

& $regasmPath $dllPath /codebase

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "====================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Registration completed!" -ForegroundColor Green
    Write-Host "====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the connection:" -ForegroundColor White
    Write-Host "     cd D:\sw2026\代码\测试代码" -ForegroundColor Yellow
    Write-Host "     py test_100_percent_automation.py" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "====================================================" -ForegroundColor Red
    Write-Host "[ERROR] Registration failed!" -ForegroundColor Red
    Write-Host "====================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - DLL file not found: $dllPath" -ForegroundColor White
    Write-Host "  - .NET Framework version mismatch" -ForegroundColor White
    Write-Host "  - Registry access denied" -ForegroundColor White
    Write-Host ""
}

Read-Host "Press Enter to exit"
