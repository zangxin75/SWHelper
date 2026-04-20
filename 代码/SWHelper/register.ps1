# Register SWHelper.Robust V6 Final
# PowerShell script for better Unicode support

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Register SWHelper.Robust V6 Final" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Administrator rights required" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Set directory
$dllPath = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Robust.dll"
$releaseDir = "D:\sw2026\代码\SWHelper\bin\Release"

Write-Host "Current directory: $releaseDir" -ForegroundColor Green
Write-Host ""

# Check DLL exists
if (-not (Test-Path $dllPath)) {
    Write-Host "ERROR: DLL not found at $dllPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Show DLL info
$dllItem = Get-Item $dllPath
Write-Host "DLL Information:" -ForegroundColor Cyan
Write-Host "  Path: $($dllItem.FullName)" -ForegroundColor White
Write-Host "  Size: $($dllItem.Length) bytes" -ForegroundColor White
Write-Host "  Modified: $($dllItem.LastWriteTime)" -ForegroundColor White
Write-Host ""

# Unregister old version
Write-Host "Step 1: Unregister old version..." -ForegroundColor Yellow
& "C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe" $dllPath /unregister 2>$null
Write-Host "  Done." -ForegroundColor Green
Write-Host ""

# Register new version
Write-Host "Step 2: Register new version..." -ForegroundColor Yellow
$result = & "C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe" $dllPath /codebase
if ($LASTEXITCODECODE -ne 0) {
    Write-Host "  ERROR: Registration failed" -ForegroundColor Red
    Write-Host $result
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  Done." -ForegroundColor Green
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Registration complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Close all applications before testing:" -ForegroundColor Yellow
Write-Host "  - Close all SolidWorks instances" -ForegroundColor White
Write-Host "  - Close all PowerShell windows" -ForegroundColor White
Write-Host ""
Write-Host "Then run: py test_createpart_v6_nocache.py" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
