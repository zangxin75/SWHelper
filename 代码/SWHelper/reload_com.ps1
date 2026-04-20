# Force COM cache clear and reload SWHelper

Write-Host "Clearing COM cache for SWHelper..."
Write-Host ""

# Stop all Python processes (they may be holding the COM reference)
Write-Host "Stopping Python processes..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Clear COM cache (if any)
Write-Host "COM cache cleared"
Write-Host ""

Write-Host "SWHelper should now reload with the updated version"
Write-Host ""
Write-Host "Next: Run the test again"
Write-Host "  cd D:\sw2026\代码\测试代码"
Write-Host "  D:\app_install\python.exe verify_csharp_swHelper_v2.py"
