# Compile 100% Version PowerShell Script
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Dynamic.100.dll"
$SRC = "Simple_Dynamic_Extended.cs"

Write-Host "Compiling 100% Version..."
Write-Host "Source: $SRC"
Write-Host "Output: $OUT"
Write-Host ""

& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation completed!"
    Write-Host "Output: $OUT"
    Write-Host ""
    Write-Host "New methods available:"
    Write-Host "  - CreateCut: Cut through holes"
    Write-Host "  - CreateInternalThread: Internal threads"
    Write-Host ""
    Write-Host "Next step: Register as Administrator"
    Write-Host "Command: regasm bin\Release\SWHelper.Dynamic.100.dll /codebase"
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed!"
    exit 1
}
