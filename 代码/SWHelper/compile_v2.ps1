# Compile SWHelper.Robust.dll - Fix plane name to English

$frameworkPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319"
$csc = Join-Path $frameworkPath "csc.exe"
$sourceFile = "SWHelper_Robust.cs"
$targetDir = "bin\Release"
$targetFile = Join-Path $targetDir "SWHelper.Robust.dll"

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Write-Host "Compiling SWHelper.Robust.dll..."
Write-Host "Source: $sourceFile"
Write-Host "Target: $targetFile"
Write-Host ""

$refs = @(
    "/reference:`"C:\Program Files\Common Files\SOLIDWORKS 2026\api\redist\SolidWorks.Interop.sldworks.dll`"",
    "/reference:`"C:\Program Files\Common Files\SOLIDWORKS 2026\api\redist\SolidWorks.Interop.swconst.dll`"",
    "/reference:`"C:\Program Files\Common Files\SOLIDWORKS 2026\api\redist\SolidWorks.Interop.swdocumentmgr.dll`"",
    "/reference:System.dll"
)

$otherParams = @(
    "/target:library",
    "/out:`"$targetFile`"",
    "/doc:`"$targetDir\SWHelper.Robust.xml`"",
    "/platform:x64",
    $sourceFile
)

$params = $refs + $otherParams

& $csc $params 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Compilation successful!"
    Write-Host ""

    Write-Host "Registering COM component..."
    & $frameworkPath\regasm.exe /codebase /tlb $targetFile 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[SUCCESS] Registration successful!"
        Write-Host ""
        Write-Host "Fixed: Plane name changed to 'Front Plane' (English)"
        Write-Host ""
        Write-Host "Next: Run verification test"
        Write-Host "  cd D:\sw2026\代码\测试代码"
        Write-Host "  D:\app_install\python.exe verify_csharp_swHelper_v2.py"
    }
} else {
    Write-Host ""
    Write-Host "[ERROR] Compilation failed"
}
