@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════
echo     Claude Code + SolidWorks Agent 部署脚本
echo ════════════════════════════════════════════════════════════
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请先安装Python 3.11+
    pause
    exit /b 1
)

echo ✓ Python环境检测通过
echo.

REM 检查SolidWorks
echo 检查SolidWorks 2026...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\SolidWorks\SOLIDWORKS 2026" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 未检测到SolidWorks 2026注册表项
    echo 请确保SolidWorks 2026已正确安装
) else (
    echo ✓ 检测到SolidWorks 2026安装
)
echo.

REM 安装依赖
echo 安装Python依赖包...
echo.

echo [1/4] 安装Anthropic Claude SDK...
pip install anthropic >nul 2>&1
if errorlevel 1 (
    echo ⚠️ anthropic安装失败
) else (
    echo ✓ anthropic安装成功
)

echo [2/4] 安装asyncio支持...
python -c "import asyncio" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ asyncio不可用
) else (
    echo ✓ asyncio可用
)

echo [3/4] 安装pywin32（COM接口）...
pip install pywin32 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ pywin32安装失败
) else (
    echo ✓ pywin32安装成功
)

echo [4/4] 验证MCP服务器...
cd /d "%~dp0项目\SolidworksMCP-python"
if exist "src\solidworks_mcp\__init__.py" (
    echo ✓ MCP服务器文件存在
) else (
    echo ❌ MCP服务器文件不存在
    cd /d "%~dp0"
    pause
    exit /b 1
)

cd /d "%~dp0"
echo.

REM 检查API密钥
echo 检查Claude API配置...
set "API_KEY=%ANTHROPIC_API_KEY%"
if "!API_KEY!"=="" (
    echo ⚠️ 未设置ANTHROPIC_API_KEY环境变量
    echo.
    echo 设置方法:
    echo 1. 访问 https://console.anthropic.com/
    echo 2. 创建API密钥
    echo 3. 设置环境变量: set ANTHROPIC_API_KEY=your-key-here
    echo.
    echo 或者使用本地模式（无需API密钥）
) else (
    echo ✓ Claude API密钥已设置
)
echo.

REM 创建启动脚本
echo 创建启动脚本...

REM 基础Agent启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0代码\Python脚本"
echo python agent_coordinator.py
) > "启动基础Agent.bat"

REM Claude增强启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0代码\Python脚本"
echo python claude_sw_integration.py
) > "启动Claude增强Agent.bat"

REM 测试脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0代码\测试代码"
echo python test_agent.py
) > "运行测试.bat"

echo ✓ 启动脚本创建完成
echo.

REM 配置完成提示
echo ════════════════════════════════════════════════════════════
echo.
echo 🎉 Claude Code + SolidWorks Agent 配置完成！
echo.
echo 📝 使用方法:
echo.
echo 1. 基础模式（无需API密钥）:
echo    双击运行: 启动基础Agent.bat
echo.
echo 2. Claude增强模式（需要API密钥）:
echo    双击运行: 启动Claude增强Agent.bat
echo.
echo 3. 运行测试:
echo    双击运行: 运行测试.bat
echo.
echo 📚 文档位置:
echo    - 实施方案: Claude_Code_SolidWorks_Agent_实施方案.md
echo    - 配置文件: 配置\agent_config.json
echo    - 代码文件: 代码\Python脚本\
echo.
echo ⚠️ 注意事项:
echo    - 确保SolidWorks 2026正在运行
echo    - 首次运行需要初始化COM接口
echo    - 建议先运行测试脚本验证环境
echo.
echo ════════════════════════════════════════════════════════════
echo.

pause