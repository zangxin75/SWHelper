# Compile Robust Version
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "============================================================================"
Write-Host "SWHelper Robust Architecture - High Reliability Version"
Write-Host "============================================================================"
Write-Host ""
Write-Host "Compiling Robust Version..."
Write-Host "Source: $SRC"
Write-Host "Output: $OUT"
Write-Host ""

& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation completed!"
    Write-Host ""
    Write-Host "Robust Architecture Features:"
    Write-Host "  - Connection Stability: Multi-retry and backup methods"
    Write-Host "  - API Reliability: Parameter validation and error handling"
    Write-Host "  - State Management: Real-time health monitoring"
    Write-Host "  - Resource Management: Proper COM cleanup"
    Write-Host ""
    Write-Host "Version: 2.0-Robust"
    Write-Host "Build: 2026.04.14"
    Write-Host ""
    Write-Host "Next step: Register as Administrator"
    Write-Host "Command: regasm bin\Release\SWHelper.Robust.dll /codebase"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed!"
    exit 1
}
