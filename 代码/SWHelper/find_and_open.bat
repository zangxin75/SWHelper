@echo off
REM ============================================================
REM 查找并定位 register_and_test.bat 文件
REM ============================================================

echo.
echo ============================================================
echo 查找 SWHelper 自动化脚本
echo ============================================================
echo.

echo 文件位置: D:\sw2026\代码\SWHelper\register_and_test.bat
echo.

REM 检查文件是否存在
if exist "D:\sw2026\代码\SWHelper\register_and_test.bat" (
    echo [OK] 文件已找到！
    echo.
    echo 文件大小:
    dir "D:\sw2026\代码\SWHelper\register_and_test.bat" | find "register_and_test.bat"
    echo.
    echo 现在打开文件位置...
    explorer.exe /select,"D:\sw2026\代码\SWHelper\register_and_test.bat"
) else (
    echo [ERROR] 文件未找到！
    echo.
    echo 请确认路径: D:\sw2026\代码\SWHelper\
    echo.
    pause
)
