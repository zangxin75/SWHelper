# 编译SWHelper.Robust.dll - 修复基准面名称
# 使用"Front Plane"而不是"前视基准面"

Write-Host "=" * 80
Write-Host "编译 SWHelper.Robust.dll - 修复基准面名称"
Write-Host "=" * 80
Write-Host ""

$frameworkPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319"
$csc = Join-Path $frameworkPath "csc.exe"
$sourceFile = "SWHelper_Robust.cs"
$targetDir = "bin\Release"
$targetFile = Join-Path $targetDir "SWHelper.Robust.dll"
$tlbFile = Join-Path $targetDir "SWHelper.Robust.tlb"

# 确保目标目录存在
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Write-Host "源文件: $sourceFile"
Write-Host "目标文件: $targetFile"
Write-Host ""

# 编译参数
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

Write-Host "编译参数:"
$params | ForEach-Object { Write-Host "  $_" }
Write-Host ""

# 执行编译
Write-Host "开始编译..."
& $csc $params 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] 编译成功!"
    Write-Host ""

    # 注册DLL
    Write-Host "注册COM组件..."
    & $frameworkPath\regasm.exe /codebase /tlb $targetFile 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[SUCCESS] 注册成功!"
        Write-Host ""
        Write-Host "修复内容:"
        Write-Host "  - 基准面名称: '前视基准面' → 'Front Plane'"
        Write-Host "  - 使用英文API名称（SolidWorks API标准）"
        Write-Host ""
        Write-Host "下一步: 运行验证测试"
        Write-Host "  cd 'D:\sw2026\代码\测试代码'"
        Write-Host "  python verify_csharp_swHelper_v2.py"
        Write-Host ""
    } else {
        Write-Host "[ERROR] 注册失败"
    }
} else {
    Write-Host ""
    Write-Host "[ERROR] 编译失败"
}
