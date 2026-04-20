# Compile Full Automation Version
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Dynamic.FullAuto.dll"
$SRC = "Simple_Dynamic_Extended_Fixed2.cs"

Write-Host "Compiling Full Automation Version..."
Write-Host "Source: $SRC"
Write-Host "Output: $OUT"
Write-Host ""

& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation completed!"
    Write-Host "Output: $OUT"
    Write-Host ""
    Write-Host "API Fixes applied:"
    Write-Host "  - Fixed CreatePart: Using correct API calls"
    Write-Host "  - Fixed SelectByID2: Correct parameter types"
    Write-Host "  - Strong typing for swApp"
    Write-Host ""
    Write-Host "Next step: Register as Administrator"
    Write-Host "Command: regasm bin\Release\SWHelper.Dynamic.FullAuto.dll /codebase"
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed!"
    exit 1
}
