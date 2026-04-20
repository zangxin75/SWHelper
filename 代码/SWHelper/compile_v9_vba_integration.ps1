# Compile SWHelper.Robust.dll - V9 with VBA macro integration
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "Compiling V9 - VBA macro integration..."
& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    $timestamp = (Get-Item $OUT).LastWriteTime
    Write-Host "DLL Timestamp: $timestamp"
    Write-Host ""

    Write-Host "V9 Key Features:"
    Write-Host "  - CreateSketchViaVBA: Uses VBA macros for sketch creation"
    Write-Host "  - Fallback: Late binding via reflection"
    Write-Host "  - Multiple plane names support"
    Write-Host "  - Bypasses C# early binding issues"
    Write-Host ""

    Write-Host "VBA Macro File: SWHelper_Macros.bas"
    Write-Host ""

    Write-Host "Installation Instructions:"
    Write-Host "  1. Open SolidWorks"
    Write-Host "  2. Tools > Macros > Edit"
    Write-Host "  3. File > Import File"
    Write-Host "  4. Select: D:\sw2026\代码\SWHelper\SWHelper_Macros.bas"
    Write-Host "  5. Save and close VBA editor"
    Write-Host ""

    Write-Host "Clearing COM cache..."
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "COM cache cleared"
    Write-Host ""
    Write-Host "Ready for V9 testing!"
    Write-Host ""
    Write-Host "IMPORTANT: Install VBA macros first!"
    Write-Host "Run: D:\app_install\python.exe test_v9_vba_integration.py"

} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
