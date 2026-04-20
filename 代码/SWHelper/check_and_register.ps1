# 检查并重新注册SWHelper DLL
# 使用方法：在PowerShell中运行此脚本

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "SWHelper DLL 检查和注册工具" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# 设置路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$dllPath = Join-Path $scriptPath "bin\Release\SWHelper.Robust.dll"
$regasmPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"

# 检查DLL文件是否存在
Write-Host "步骤1: 检查DLL文件..." -ForegroundColor Yellow
if (Test-Path $dllPath) {
    $dllInfo = Get-Item $dllPath
    Write-Host "[OK] 找到DLL文件: $($dllInfo.Name)" -ForegroundColor Green
    Write-Host "     修改时间: $($dllInfo.LastWriteTime)" -ForegroundColor Gray
    Write-Host "     文件大小: $($dllInfo.Length) bytes" -ForegroundColor Gray
    Write-Host ""

    # 检查是否是最新编译的（最近5分钟内）
    $minutesSinceCompile = (Get-Date) - $dllInfo.LastWriteTime
    if ($minutesSinceCompile.TotalMinutes -lt 5) {
        Write-Host "[INFO] DLL是刚刚编译的（$([int]$minutesSinceCompile.TotalMinutes)分钟前）" -ForegroundColor Cyan
    } else {
        Write-Host "[WARN] DLL可能不是最新版本（编译于$([int]$minutesSinceCompile.TotalMinutes)分钟前）" -ForegroundColor Yellow
        Write-Host "       建议重新编译: powershell -File compile_robust.ps1" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] DLL文件不存在: $dllPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先运行编译脚本:" -ForegroundColor Yellow
    Write-Host "  cd 'D:\sw2026\代码\SWHelper'" -ForegroundColor Gray
    Write-Host "  powershell -File compile_robust.ps1" -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

Write-Host ""

# 检查管理员权限
Write-Host "步骤2: 检查管理员权限..." -ForegroundColor Yellow
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARN] 当前没有管理员权限" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "需要管理员权限来注册DLL。请选择:" -ForegroundColor Yellow
    Write-Host "  1. 以管理员身份重新运行PowerShell，然后执行此脚本" -ForegroundColor Cyan
    Write-Host "  2. 或者右键点击 register_admin.bat，选择'以管理员身份运行'" -ForegroundColor Cyan
    Write-Host ""

    $response = Read-Host "是否尝试提升权限注册？(Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host ""
        Write-Host "尝试使用UAC提示注册..." -ForegroundColor Cyan
        try {
            Start-Process regasm -ArgumentList "`"$dllPath`" /codebase /tlb" -Verb RunAs -Wait
            Write-Host "[OK] 注册命令已执行" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] 注册失败: $_" -ForegroundColor Red
            pause
            exit 1
        }
    } else {
        Write-Host "[INFO] 跳过DLL注册" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "手动注册方法:" -ForegroundColor Yellow
        Write-Host "  1. 以管理员身份打开命令提示符" -ForegroundColor Gray
        Write-Host "  2. 执行: $regasmPath `"$dllPath`" /codebase" -ForegroundColor Gray
        Write-Host ""
        pause
        exit 1
    }
} else {
    Write-Host "[OK] 已获得管理员权限" -ForegroundColor Green
    Write-Host ""

    # 先尝试卸载旧版本
    Write-Host "步骤3: 卸载旧版本..." -ForegroundColor Yellow
    & $regasmPath "$dllPath" /unregister 2>$null
    if ($?) {
        Write-Host "[OK] 旧版本已卸载" -ForegroundColor Green
    } else {
        Write-Host "[INFO] 没有旧版本或卸载失败（这是正常的）" -ForegroundColor Cyan
    }
    Write-Host ""

    # 注册新版本
    Write-Host "步骤4: 注册新版本..." -ForegroundColor Yellow
    Write-Host "执行: $regasmPath `"$dllPath`" /codebase /tlb" -ForegroundColor Gray
    Write-Host ""

    & $regasmPath "$dllPath" /codebase /tlb

    if ($?) {
        Write-Host ""
        Write-Host "============================================================================" -ForegroundColor Green
        Write-Host "[SUCCESS] DLL注册成功！" -ForegroundColor Green
        Write-Host "============================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "下一步:" -ForegroundColor Cyan
        Write-Host "  1. 确保SolidWorks 2026正在运行" -ForegroundColor Gray
        Write-Host "  2. 运行测试: cd 'D:\sw2026\代码\测试代码'" -ForegroundColor Gray
        Write-Host "  3.         python verify_createsketch_fix.py" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "============================================================================" -ForegroundColor Red
        Write-Host "[ERROR] DLL注册失败" -ForegroundColor Red
        Write-Host "============================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "可能的原因:" -ForegroundColor Yellow
        Write-Host "  - DLL文件被占用（关闭SolidWorks和Python）" -ForegroundColor Gray
        Write-Host "  - 注册表权限问题" -ForegroundColor Gray
        Write-Host "  - .NET Framework版本不匹配" -ForegroundColor Gray
        Write-Host ""
    }
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
