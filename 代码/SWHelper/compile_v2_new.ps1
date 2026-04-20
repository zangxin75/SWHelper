# Compile SWHelper.Robust.V2.dll with new ProgID
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.V2.dll"
$SRC = "SWHelper_Robust_V2.cs"
$TLB = "bin\Release\SWHelper.Robust.V2.tlb"

Write-Host "Compiling SWHelper.Robust.V2.dll (new ProgID to bypass cache)..."
& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    Write-Host "Registering as new COM component..."
    $regasm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
    & $regasm /codebase /tlb $OUT 2>&1 | Out-Null

    Write-Host "[SUCCESS] Registration completed!"
    Write-Host ""
    Write-Host "New ProgID: SWHelper.SWHelperRobustV2"
    Write-Host ""
    Write-Host "Next: Create test script for V2"
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
