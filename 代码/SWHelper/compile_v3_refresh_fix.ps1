# Compile SWHelper.Robust.dll - V3 with RefreshModel fix
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "Compiling V3 - RefreshModel fix..."
& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    # Get file timestamp
    $timestamp = (Get-Item $OUT).LastWriteTime
    Write-Host "DLL Timestamp: $timestamp"
    Write-Host ""

    Write-Host "Fixes in V3:"
    Write-Host "  - Improved RefreshModel with document type checking"
    Write-Host "  - Safer COM object release"
    Write-Host "  - Better exception handling"
    Write-Host "  - SketchManager only for part documents"
    Write-Host ""

    Write-Host "Testing now..."

} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
