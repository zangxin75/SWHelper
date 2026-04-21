# SWHelper GitHub 推送脚本
# 请替换 YOUR_USERNAME 为你的 GitHub 用户名

Write-Host "================================" -ForegroundColor Green
Write-Host "SWHelper 推送到 GitHub" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 检查是否在正确的目录
if (Test-Path "README.md") {
    Write-Host "✅ 在项目根目录" -ForegroundColor Green
} else {
    Write-Host "❌ 错误: 请在项目根目录 (D:\sw2026) 运行此脚本" -ForegroundColor Red
    exit 1
}

# 获取GitHub用户名
$username = Read-Host "请输入你的 GitHub 用户名"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ 用户名不能为空" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "准备推送到: https://github.com/$username/SWHelper.git" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "确认继续? (Y/n)"

if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "步骤 1: 添加远程仓库" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

# 移除已存在的origin
git remote remove origin 2>$null

# 添加新的远程仓库
git remote add origin "https://github.com/$username/SWHelper.git"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 远程仓库添加成功" -ForegroundColor Green
} else {
    Write-Host "❌ 添加远程仓库失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "步骤 2: 推送代码到 GitHub" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "即将提示输入凭据:" -ForegroundColor Yellow
Write-Host "  用户名: $username" -ForegroundColor Yellow
Write-Host "  密码: 粘贴你的 Personal Access Token (不是登录密码!)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Token创建地址: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host ""

Pause

Write-Host ""
Write-Host "正在推送..." -ForegroundColor Yellow
Write-Host ""

# 推送代码
git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ 推送成功!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问你的仓库:" -ForegroundColor Cyan
    Write-Host "  https://github.com/$username/SWHelper" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Red
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. GitHub上尚未创建仓库" -ForegroundColor White
    Write-Host "  2. Token无效或过期" -ForegroundColor White
    Write-Host "  3. 用户名错误" -ForegroundColor White
    Write-Host "  4. 网络连接问题" -ForegroundColor White
    Write-Host ""
    Write-Host "请检查:" -ForegroundColor Yellow
    Write-Host "  - 是否已在 https://github.com/new 创建仓库" -ForegroundColor White
    Write-Host "  - Token是否正确创建并复制" -ForegroundColor White
    Write-Host "  - 用户名是否正确" -ForegroundColor White
    Write-Host ""
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
