# Clean all SWHelper versions and re-register
# Run as Administrator

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Clean All SWHelper Versions and Re-register" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] Run as Administrator" -ForegroundColor Red
    pause
    exit 1
}

$regasm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
$baseDir = "D:\sw2026\代码\SWHelper"

# Stop processes
Write-Host "Step 1: Stop all processes" -ForegroundColor Yellow
Stop-Process -Name "SLDWORKS","SLDPWORKS" -Force -ErrorAction SilentlyContinue
Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Done" -ForegroundColor Green
Write-Host ""

# Unregister all versions
Write-Host "Step 2: Unregister all SWHelper versions" -ForegroundColor Yellow

$dllFiles = @(
    "bin\Release\SWHelper.Robust.dll",
    "bin\Release\SWHelper.Dynamic.dll",
    "SWHelper.Simple.dll"
)

foreach ($dll in $dllFiles) {
    $dllPath = Join-Path $baseDir $dll
    if (Test-Path $dllPath) {
        Write-Host "Unregistering: $dll"
        & $regasm $dllPath /unregister 2>$null
    }
}

Write-Host "[OK] Done" -ForegroundColor Green
Write-Host ""

# Delete type libraries
Write-Host "Step 3: Delete type libraries" -ForegroundColor Yellow
Get-ChildItem "$baseDir\bin\Release" -Filter "*.tlb" | ForEach-Object {
    Write-Host "Deleting: $($_.Name)"
    Remove-Item $_.FullName -Force
}
Write-Host "[OK] Done" -ForegroundColor Green
Write-Host ""

# Wait for cache to clear
Write-Host "Step 4: Wait for COM cache to clear" -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "[OK] Done" -ForegroundColor Green
Write-Host ""

# Register new version
Write-Host "Step 5: Register SWHelper.Robust" -ForegroundColor Yellow
$dllPath = Join-Path $baseDir "bin\Release\SWHelper.Robust.dll"
Write-Host "DLL: $dllPath"
& $regasm $dllPath /codebase /tlb

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] SWHelper.Robust registered!" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT:" -ForegroundColor Yellow
    Write-Host "1. Close THIS PowerShell window" -ForegroundColor Yellow
    Write-Host "2. Open a NEW PowerShell window" -ForegroundColor Yellow
    Write-Host "3. Start SolidWorks 2026" -ForegroundColor Yellow
    Write-Host "4. Run test: python test_ref_fix.py" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[ERROR] Registration failed" -ForegroundColor Red
}

pause
