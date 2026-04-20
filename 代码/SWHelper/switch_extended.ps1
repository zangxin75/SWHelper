# Switch to Extended Version
# Run as Administrator

Write-Host "=============================================="
Write-Host "Switch to SWHelper Extended Version"
Write-Host "=============================================="
Write-Host ""

# Check admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Administrator privileges required!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:"
    Write-Host "  1. Right-click PowerShell"
    Write-Host "  2. Select 'Run as Administrator'"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Administrator privileges obtained" -ForegroundColor Green
Write-Host ""

# Set paths
$dllDir = "D:\sw2026\代码\SWHelper\bin\Release"
$baseDll = Join-Path $dllDir "SWHelper.Dynamic.dll"
$extendedDll = Join-Path $dllDir "SWHelper.Dynamic.Extended.dll"
$regasm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"

# Check files
if (-not (Test-Path $extendedDll)) {
    Write-Host "ERROR: Extended DLL not found!" -ForegroundColor Red
    Write-Host "Location: $extendedDll"
    Write-Host ""
    Write-Host "Please run compile_extended.bat first"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Extended DLL found" -ForegroundColor Green
Write-Host ""

# Step 1: Unregister base version
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Step 1/3: Unregister Base Version" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Unregistering: $baseDll"
& $regasm $baseDll /u *> $null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Base version unregistered" -ForegroundColor Green
} else {
    Write-Host "[INFO] Base version was not registered" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Register extended version
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Step 2/3: Register Extended Version" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Registering: $extendedDll"
& $regasm $extendedDll /codebase

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Registration failed!" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[OK] Extended version registered" -ForegroundColor Green
Write-Host ""

# Step 3: Verify
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Step 3/3: Verify Registration" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking registry..."
$classPath = "HKCR:\SWHelper.SWHelperDynamic"
if (Test-Path $classPath) {
    Write-Host "[OK] COM class registered" -ForegroundColor Green
} else {
    Write-Host "[WARNING] COM class not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Switch Complete!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Version: Extended (v1.1)"
Write-Host "New Features:"
Write-Host "  [NEW] DrawCircle"
Write-Host "  [NEW] DrawLine"
Write-Host "  [NEW] CreateRevolution"
Write-Host "  [NEW] CreateFillet"
Write-Host "  [NEW] CreateChamfer"
Write-Host ""

Write-Host "Next Steps:"
Write-Host "  1. Verify: python D:\sw2026\代码\测试代码\quick_verify.py"
Write-Host "  2. Test: python D:\sw2026\代码\测试代码\create_m5_screw.py"
Write-Host ""

Read-Host "Press Enter to exit"
