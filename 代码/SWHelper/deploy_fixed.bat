@echo off
echo ============================================================
echo 部署修复后的 SWHelper.Robust
echo ============================================================
echo.

cd /d "%~dp0bin\Release"

echo 步骤1: 检查文件
echo.
echo 需要的文件:
dir /b SWHelper.Robust.dll 2>nul
if errorlevel 1 (
    echo [错误] SWHelper.Robust.dll 不存在
    pause
    exit /b 1
)
dir /b SolidWorks.Interop.sldworks.dll 2>nul
if errorlevel 1 (
    echo [错误] SolidWorks.Interop.sldworks.dll 不存在
    echo 正在复制...
    copy "D:\app_install\solidworks2026\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll" .
)
dir /b SolidWorks.Interop.swconst.dll 2>nul
if errorlevel 1 (
    echo [错误] SolidWorks.Interop.swconst.dll 不存在
    echo 正在复制...
    copy "D:\app_install\solidworks2026\SOLIDWORKS\api\redist\SolidWorks.Interop.swconst.dll" .
)

echo.
echo 步骤2: 卸载旧版本（如果存在）
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister 2>nul

echo.
echo 步骤3: 注册新版本
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase /tlb:SWHelper.Robust.tlb

if errorlevel 1 (
    echo.
    echo [错误] 注册失败
    echo 请确保以管理员身份运行此脚本
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 部署完成！
echo ============================================================
echo.
echo 下一步:
echo   1. 关闭所有 SolidWorks 实例
echo   2. 关闭所有 PowerShell 窗口
echo   3. 启动 SolidWorks 2026
echo   4. 手动创建一个新零件
echo   5. 运行测试: py test_createsketch_only.py
echo.
pause
