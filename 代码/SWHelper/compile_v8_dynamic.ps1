# Compile SWHelper.Robust.dll - V8 with dynamic late binding
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "Compiling V8 - Dynamic late binding..."
& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    $timestamp = (Get-Item $OUT).LastWriteTime
    Write-Host "DLL Timestamp: $timestamp"
    Write-Host ""

    Write-Host "V8 Key Features:"
    Write-Host "  - Uses 'dynamic' keyword for late binding"
    Write-Host "  - Avoids early binding type checking issues"
    Write-Host "  - Similar to VBA's late binding approach"
    Write-Host "  - Can handle SOLIDWORKS 2026 API changes"
    Write-Host ""

    Write-Host "Clearing COM cache..."
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "COM cache cleared"
    Write-Host ""
    Write-Host "Ready for V8 testing!"
    Write-Host ""
    Write-Host "Run: D:\app_install\python.exe test_createsketch_manual.py"

} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
