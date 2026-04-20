# Clear COM cache and test V3
Write-Host "Clearing COM cache..."

# Stop all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait for COM to release
Start-Sleep -Seconds 3

Write-Host "COM cache cleared"
Write-Host ""
Write-Host "New DLL (V3) features:"
Write-Host "  - Document type checking in RefreshModel"
Write-Host "  - Safe COM object release"
Write-Host "  - SketchManager only for part documents"
Write-Host "  - Better exception handling"
Write-Host ""
Write-Host "Ready for testing!"
Write-Host ""
Write-Host "Next:"
Write-Host "  1. In SolidWorks: File -> New -> Part"
Write-Host "  2. Run: D:\app_install\python.exe test_createsketch_manual.py"
