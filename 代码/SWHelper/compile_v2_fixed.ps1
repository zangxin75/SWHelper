# Compile SWHelper.Robust.dll - Fixed plane name to English
$SW_API = "d:\app_install\solidworks2026\SOLIDWORKS\api\redist"
$CSC = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$OUT = "bin\Release\SWHelper.Robust.dll"
$SRC = "SWHelper_Robust.cs"

Write-Host "Compiling with English plane names..."
Write-Host "Source: $SRC"
Write-Host "Output: $OUT"
Write-Host ""

& $CSC /target:library /out:$OUT /lib:$SW_API /reference:SolidWorks.Interop.sldworks.dll /reference:SolidWorks.Interop.swconst.dll /reference:System.dll /reference:System.Core.dll /nologo $SRC 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    Write-Host "Registering COM component..."
    $regasm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
    & $regasm /codebase /tlb $OUT 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[SUCCESS] Registration successful!"
        Write-Host ""
        Write-Host "Fix applied:"
        Write-Host "  - Changed '前视基准面' → 'Front Plane'"
        Write-Host "  - Using English API names (SolidWorks standard)"
        Write-Host ""
        Write-Host "Next: Run verification test"
        Write-Host "  cd D:\sw2026\代码\测试代码"
        Write-Host "  D:\app_install\python.exe verify_csharp_swHelper_v2.py"
    } else {
        Write-Host "[ERROR] Registration failed"
    }
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
