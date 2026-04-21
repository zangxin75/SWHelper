# SWHelper 最终推送脚本 - zangxin75
Write-Host "================================" -ForegroundColor Green
Write-Host "推送到 GitHub" -ForegroundColor Green
Write-Host "用户: zangxin75" -ForegroundColor Green
Write-Host "仓库: SWHelper" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 检查当前目录
if (-not (Test-Path "README.md")) {
    Write-Host "❌ 错误: 请在项目根目录 (D:\sw2026) 运行此脚本" -ForegroundColor Red
    Read-Host "按 Enter 退出"
    exit 1
}

Write-Host "✅ 在项目根目录" -ForegroundColor Green
Write-Host ""

# 检查远程仓库
$remoteUrl = git remote get-url origin 2>$null

if ($remoteUrl -match "github.com[:/]zangxin75/SWHelper") {
    Write-Host "✅ 远程仓库已配置: $remoteUrl" -ForegroundColor Green
} else {
    Write-Host "设置远程仓库..." -ForegroundColor Yellow
    git remote add origin https://github.com/zangxin75/SWHelper.git 2>$null
    git remote set-url origin https://github.com/zangxin75/SWHelper.git
    Write-Host "✅ 远程仓库已设置" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "准备推送到 GitHub" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "仓库URL:" -ForegroundColor White
Write-Host "  https://github.com/zangxin75/SWHelper" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示:" -ForegroundColor Yellow
Write-Host "  推送时需要输入 GitHub 凭据:" -ForegroundColor White
Write-Host "  用户名: zangxin75" -ForegroundColor White
Write-Host "  密码: Personal Access Token (不是登录密码!)" -ForegroundColor Red
Write-Host ""
Write-Host "如需创建 Token:" -ForegroundColor Yellow
Write-Host "  https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host "  权限: 勾选 'repo'" -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "开始推送? (Y/n)"
if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "正在推送代码..." -ForegroundColor Yellow
Write-Host ""

# 设置Git凭据辅助
git config --global credential.helper manager-core 2>$null

# 推送代码
$pushResult = git push -u origin master 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ 推送成功！" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问你的仓库:" -ForegroundColor Cyan
    Write-Host "  https://github.com/zangxin75/SWHelper" -ForegroundColor White
    Write-Host ""

    # 打开浏览器
    Start-Process "https://github.com/zangxin75/SWHelper"

    Write-Host "正在打开浏览器..." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Red
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. Token 无效或未创建" -ForegroundColor White
    Write-Host "  2. 用户名或密码错误" -ForegroundColor White
    Write-Host "  3. 仓库尚未在 GitHub 创建" -ForegroundColor White
    Write-Host "  4. 网络连接问题" -ForegroundColor White
    Write-Host ""
    Write-Host "解决方法:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "方法1 - 在 GitHub 创建仓库后重试:" -ForegroundColor White
    Write-Host "  1. 访问: https://github.com/new" -ForegroundColor Cyan
    Write-Host "  2. 仓库名: SWHelper" -ForegroundColor Cyan
    Write-Host "  3. 不要勾选 'Add README'" -ForegroundColor Cyan
    Write-Host "  4. 重新运行此脚本" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "方法2 - 使用 GitHub CLI:" -ForegroundColor White
    Write-Host "  gh auth login" -ForegroundColor Cyan
    Write-Host "  gh repo create SWHelper --public --source=. --remote=origin --push" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
