# Compile SWHelper.Robust.dll - V7 with multiple plane names
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "Compiling V7 - Multiple plane names + detailed diagnostics..."
& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    $timestamp = (Get-Item $OUT).LastWriteTime
    Write-Host "DLL Timestamp: $timestamp"
    Write-Host ""

    Write-Host "V7 Key Features:"
    Write-Host "  - Tries 5 different plane names:"
    Write-Host "    1. Front Plane (English)"
    Write-Host "    2. 前视基准面 (Chinese)"
    Write-Host "    3. Plane1 (Numeric)"
    Write-Host "    4. 基准面1 (Chinese numeric)"
    Write-Host "    5. Front (Short English)"
    Write-Host "  - Detailed diagnostic info for each attempt"
    Write-Host "  - Preserves full error history"
    Write-Host ""

    Write-Host "Clearing COM cache..."
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "COM cache cleared"
    Write-Host ""
    Write-Host "Ready for V7 testing!"
    Write-Host ""
    Write-Host "Run: D:\app_install\python.exe test_createsketch_manual.py"

} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
