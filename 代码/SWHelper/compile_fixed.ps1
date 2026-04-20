# Compile Fixed Version
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Dynamic.Fixed.dll"
$SRC = "Simple_Dynamic_Extended_Fixed.cs"

Write-Host "Compiling Fixed Version..."
Write-Host "Source: $SRC"
Write-Host "Output: $OUT"
Write-Host ""

& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation completed!"
    Write-Host "Output: $OUT"
    Write-Host ""
    Write-Host "Fix applied:"
    Write-Host "  - Removed GetUserPreferenceStringValue call"
    Write-Host "  - Using default template"
    Write-Host ""
    Write-Host "Next step: Register as Administrator"
    Write-Host "Command: regasm bin\Release\SWHelper.Dynamic.Fixed.dll /codebase"
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed!"
    exit 1
}
