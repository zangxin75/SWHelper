# Register SWHelper.Robust.dll - Run as Administrator
$DLL = "bin\Release\SWHelper.Robust.dll"
$regasm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"

Write-Host "Registering SWHelper.Robust.dll..."
Write-Host "File: $DLL"
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator"
    Write-Host ""
    Write-Host "To run as Administrator:"
    Write-Host "  1. Right-click PowerShell"
    Write-Host "  2. Select 'Run as Administrator'"
    Write-Host "  3. Run this script again"
    exit 1
}

& $regasm /codebase /tlb $DLL

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Registration completed!"
    Write-Host ""
    Write-Host "Next: Test the updated DLL"
    Write-Host "  cd D:\sw2026\代码\测试代码"
    Write-Host "  D:\app_install\python.exe verify_csharp_swHelper_v2.py"
} else {
    Write-Host ""
    Write-Host "[ERROR] Registration failed"
}
