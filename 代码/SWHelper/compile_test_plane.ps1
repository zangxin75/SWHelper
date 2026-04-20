# Compile TestPlaneName.cs
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$SRC = "TestPlaneName.cs"
$OUT = "TestPlaneName.exe"

Write-Host "Compiling plane name test..."
& $CSC /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /out:$OUT $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""
    Write-Host "Next: Run the test"
    Write-Host "  Make sure SolidWorks is running with a part document open"
    Write-Host "  Then run: .\TestPlaneName.exe"
} else {
    Write-Host "[ERROR] Compilation failed"
}
