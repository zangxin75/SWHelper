# Compile SWHelper.Robust.dll - V6 with multiple SketchManager access methods
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "Compiling V6 - Multiple SketchManager access methods..."
& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    $timestamp = (Get-Item $OUT).LastWriteTime
    Write-Host "DLL Timestamp: $timestamp"
    Write-Host ""

    Write-Host "V6 Key Features:"
    Write-Host "  - Method 1: Direct SketchManager access"
    Write-Host "  - Method 2: Interface casting"
    Write-Host "  - Method 3: Reflection-based access"
    Write-Host "  - Tries all methods before giving up"
    Write-Host ""

    Write-Host "Clearing COM cache..."
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "COM cache cleared"
    Write-Host ""
    Write-Host "Ready for V6 testing!"
    Write-Host ""
    Write-Host "Run: D:\app_install\python.exe test_createsketch_manual.py"

} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
