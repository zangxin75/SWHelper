# Force Re-register SWHelper DLL - 清除COM缓存
# 必须以管理员身份运行

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "SWHelper DLL - 强制重新注册（清除COM缓存）" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] 请以管理员身份运行此脚本" -ForegroundColor Red
    pause
    exit 1
}

$regasm = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe"
$dll = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Robust.dll"
$tlb = "D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Robust.tlb"

Write-Host "步骤1: 停止所有SolidWorks进程..." -ForegroundColor Yellow
Stop-Process -Name "SLDWORKS" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "SLDPWORKS" -Force -ErrorAction SilentlyContinue
Write-Host "[OK] 进程已停止" -ForegroundColor Green
Write-Host ""

Write-Host "步骤2: 停止所有Python进程..." -ForegroundColor Yellow
Get-Process python | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python3 | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "[OK] Python进程已停止" -ForegroundColor Green
Write-Host ""

# 等待进程完全结束
Start-Sleep -Seconds 2

Write-Host "步骤3: 注销旧版本DLL..." -ForegroundColor Yellow
& $regasm $dll /unregister 2>$null
if (Test-Path $tlb) {
    Remove-Item $tlb -Force
    Write-Host "[OK] 类型库文件已删除" -ForegroundColor Green
}
Write-Host "[OK] 注销完成" -ForegroundColor Green
Write-Host ""

Write-Host "步骤4: 等待COM缓存释放..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "[OK] 等待完成" -ForegroundColor Green
Write-Host ""

Write-Host "步骤5: 重新生成类型库..." -ForegroundColor Yellow
if (Test-Path $tlb) {
    Remove-Item $tlb -Force -ErrorAction SilentlyContinue
}
Write-Host "[OK] 完成" -ForegroundColor Green
Write-Host ""

Write-Host "步骤6: 注册新版本DLL..." -ForegroundColor Yellow
& $regasm $dll /codebase /tlb

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] DLL注册成功！" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步操作（重要！）：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 完全关闭此PowerShell窗口" -ForegroundColor Yellow
    Write-Host "2. 打开一个新的PowerShell窗口（非管理员）" -ForegroundColor Yellow
    Write-Host "3. 启动SolidWorks 2026" -ForegroundColor Yellow
    Write-Host "4. 运行测试：" -ForegroundColor Yellow
    Write-Host "   cd 'D:\sw2026\代码\测试代码'" -ForegroundColor Gray
    Write-Host "   & 'D:\app_install\python.exe' verify_createsketch_fix.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "注意：必须使用新的PowerShell窗口！" -ForegroundColor Red
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] 注册失败" -ForegroundColor Red
    Write-Host ""
}

pause
