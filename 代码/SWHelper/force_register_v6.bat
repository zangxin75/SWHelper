@echo off
echo ============================================================
echo 强制重新注册 SWHelper.Robust V6
echo ============================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] 需要管理员权限
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

cd /d "%~dp0bin\Release"

echo 当前目录: %CD%
echo.

echo 步骤1: 检查 DLL 文件...
dir SWHelper.Robust.dll | findstr "SWHelper.Robust.dll"
if errorlevel 1 (
    echo [ERROR] DLL 文件不存在
    pause
    exit /b 1
)
echo.

echo 步骤2: 完全卸载旧版本...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /unregister
if errorlevel 1 (
    echo WARN - 卸载失败（可能未注册）
)
echo.

echo 步骤3: 删除类型库（如果存在）...
if exist SWHelper.Robust.tlb (
    del SWHelper.Robust.tlb
    echo 已删除旧的类型库
)
echo.

echo 步骤4: 注册新版本...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /codebase /tlb:SWHelper.Robust.tlb
if errorlevel 1 (
    echo.
    echo [ERROR] 注册失败
    pause
    exit /b 1
)
echo.

echo 步骤5: 验证注册...
C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe SWHelper.Robust.dll /regfile:temp.reg
if errorlevel 1 (
    echo [ERROR] 验证失败
    pause
    exit /b 1
)

echo 注册文件已生成: temp.reg
echo.

echo 步骤6: 清理临时文件...
del temp.reg
echo.

echo ============================================================
echo 注册完成！
echo ============================================================
echo.
echo DLL 信息:
dir SWHelper.Robust.dll | findstr "SWHelper.Robust.dll"
echo.
echo 下一步:
echo   1. 关闭所有 SolidWorks 实例
echo   2. 关闭所有 PowerShell 窗口
echo   3. 启动 SolidWorks 2026
echo   4. 运行: py test_createpart_v6.py
echo.
pause
