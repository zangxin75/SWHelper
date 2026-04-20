@echo off
REM ============================================================
REM 一键注册脚本 - 请右键以管理员身份运行
REM ============================================================

echo.
echo ========================================================================
echo SWHelper.Dynamic.dll - 一键注册
echo ========================================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 需要管理员权限！
    echo.
    echo 请按以下步骤操作：
    echo   1. 右键点击此文件
    echo   2. 选择 "以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [OK] 已获得管理员权限
echo.

REM 设置路径
set DLL_PATH=D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Dynamic.dll
set REGASM=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe

REM 检查DLL文件
if not exist "%DLL_PATH%" (
    echo [ERROR] 找不到DLL文件！
    echo 期望位置: %DLL_PATH%
    pause
    exit /b 1
)

echo [OK] DLL文件存在
echo.

REM 注册COM组件
echo ========================================================================
echo 正在注册COM组件...
echo ========================================================================
echo.

"%REGASM%" "%DLL_PATH%" /codebase /tlb:"D:\sw2026\代码\SWHelper\bin\Release\SWHelper.Dynamic.tlb"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 注册失败！
    echo 错误代码: %errorlevel%
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo 验证注册...
echo ========================================================================
echo.

reg query "HKCR\SWHelper.SWHelperDynamic" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] COM类已注册: SWHelper.SWHelperDynamic
) else (
    echo [WARNING] COM类未找到（可能不影响功能）
)

reg query "HKCR\SWHelper.ISWHelperDynamic" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] COM接口已注册: SWHelper.ISWHelperDynamic
) else (
    echo [WARNING] COM接口未找到（可能不影响功能）
)

echo.
echo ========================================================================
echo 注册完成！
echo ========================================================================
echo.
echo 下一步：
echo   1. 打开Python
echo   2. 运行测试: python D:\sw2026\代码\测试代码\verify_com_component.py
echo.
echo 或者直接在Python中测试：
echo   import win32com.client
echo   helper = win32com.client.Dispatch("SWHelper.SWHelperDynamic")
echo   print(helper.GetVersion())
echo.
pause
