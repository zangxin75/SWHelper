# Simple DLL Registration Script
# Usage: Run as Administrator

$dllPath = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Robust.dll"
$regasmPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SWHelper DLL Registration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] Please run as Administrator" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if DLL exists
if (-not (Test-Path $dllPath)) {
    Write-Host "[ERROR] DLL not found: $dllPath" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[OK] DLL found" -ForegroundColor Green
Write-Host ""

# Unregister old version
Write-Host "Step 1: Unregistering old version..." -ForegroundColor Yellow
& $regasmPath $dllPath /unregister 2>$null
Write-Host "[OK] Done" -ForegroundColor Green
Write-Host ""

# Register new version
Write-Host "Step 2: Registering new version..." -ForegroundColor Yellow
Write-Host "Command: $regasmPath $dllPath /codebase /tlb" -ForegroundColor Gray
& $regasmPath $dllPath /codebase /tlb

if ($?) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[SUCCESS] DLL Registered!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start SolidWorks 2026" -ForegroundColor Gray
    Write-Host "2. Run test: cd D:\sw2026\Code\TestCode" -ForegroundColor Gray
    Write-Host "3. python verify_createsketch_fix.py" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Registration failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try closing SolidWorks and Python first" -ForegroundColor Yellow
}

Write-Host ""
pause
