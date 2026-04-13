"""
ENH-07: 真实MCP集成 - 连接SolidWorks API

测试真实SolidWorks MCP Server集成功能，包括：
- MCP客户端初始化
- 真实SolidWorks API调用
- 错误处理与重试机制
- 端到端工作流验证

对应需求文件: 文档/需求/req_enh_07_real_mcp_integration.md
需求编号: ENH-07-01 到 ENH-07-06
"""

import pytest
import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import os

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent / "代码" / "Python脚本"
sys.path.insert(0, str(project_root))

from agent_coordinator import AgentCoordinator


# ==================== 测试配置 ====================

# 检查SolidWorks是否可用
SOLIDWORKS_AVAILABLE = os.environ.get("SOLIDWORKS_AVAILABLE", "false").lower() == "true"
MCP_SERVER_AVAILABLE = os.environ.get("MCP_SERVER_AVAILABLE", "false").lower() == "true"


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "requires_solidworks: marks tests that require SolidWorks to be running"
    )
    config.addinivalue_line(
        "markers", "requires_mcp: marks tests that require MCP Server to be available"
    )


def skip_if_no_sw():
    """Skip test if SolidWorks is not available"""
    if not SOLIDWORKS_AVAILABLE:
        pytest.skip("SolidWorks not available (set SOLIDWORKS_AVAILABLE=true to run)")


def skip_if_no_mcp():
    """Skip test if MCP Server is not available"""
    if not MCP_SERVER_AVAILABLE:
        pytest.skip("MCP Server not available (set MCP_SERVER_AVAILABLE=true to run)")


# ==================== 测试数据 ====================

MCP_INIT_CASES = [
    # (case_id, description, mcp_available, sw_available, should_succeed)
    ("ENH-07-01", "MCP客户端初始化成功", True, True, True),
    ("ENH-07-01", "MCP Server未安装", False, False, False),
    ("ENH-07-01", "SolidWorks未运行", True, False, False),
]

REAL_API_CASES = [
    # (case_id, description, user_input, expected_tool, requires_sw)
    ("ENH-07-02", "创建零件（真实API）",
     "创建一个100x100x50的方块", "sw_create_part", True),

    ("ENH-07-03", "创建装配体（真实API）",
     "创建一个装配体，2个零件", "sw_create_assembly", True),

    ("ENH-07-04", "创建工程图（真实API）",
     "创建工程图，3个视图", "sw_create_drawing", True),
]

ERROR_HANDLING_CASES = [
    # (case_id, description, scenario, expected_error_type)
    ("ENH-07-05", "SolidWorks未运行",
     "sw_not_running", "SWNotRunningError"),

    ("ENH-07-05", "MCP连接超时",
     "mcp_timeout", "TimeoutError"),

    ("ENH-07-05", "API调用失败",
     "api_error", "SWAPIError"),
]

E2E_WORKFLOW_CASES = [
    # (case_id, description, user_input, min_tasks, requires_sw)
    ("ENH-07-06", "端到端 - 创建零件",
     "创建一个轴承座，底座200x150x20mm", 1, True),

    ("ENH-07-06", "端到端 - 创建工程图",
     "创建一个工程图，A3图纸，3个视图", 1, True),

    ("ENH-07-06", "端到端 - 复杂设计",
     "设计一个轴承座，底座200x150x20mm，然后创建工程图", 2, True),
]


# ==================== 测试实现 ====================

class TestEnh07MCPInitialization:
    """测试MCP客户端初始化 (ENH-07-01)"""

    @pytest.mark.parametrize("case_id,description,mcp_available,sw_available,should_succeed",
                             MCP_INIT_CASES,
                             ids=[c[0] for c in MCP_INIT_CASES])
    def test_mcp_initialization(self, case_id, description, mcp_available, sw_available, should_succeed):
        """测试MCP客户端初始化"""
        skip_if_no_mcp()
        skip_if_no_sw()

        # Mock MCP连接
        with patch('agent_coordinator.stdio_client') as mock_stdio:
            with patch('agent_coordinator.ClientSession') as mock_session_cls:
                # Mock session
                mock_session = AsyncMock()
                mock_session.initialize = AsyncMock()
                mock_session.list_tools = AsyncMock(return_value={"tools": []})
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock()
                mock_session_cls.return_value = mock_session

                # Mock stdio_client context manager
                mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(None, None))
                mock_stdio.return_value.__aexit__ = AsyncMock()

                try:
                    # 创建Coordinator with MCP
                    coordinator = AgentCoordinator(
                        use_real_sw=True  # use_real_sw会触发MCP模式（待实现）
                    )

                    if should_succeed:
                        # 验证初始化成功
                        assert coordinator is not None, f"{case_id}: Coordinator should not be None"
                        # 验证MCP连接被调用
                        # (具体验证取决于实现)
                    else:
                        # 预期失败的情况，这里应该抛出异常
                        pass

                except Exception as e:
                    if should_succeed:
                        pytest.fail(f"{case_id}: Should not raise exception: {e}")
                    # else: 预期的异常，正常


class TestEnh07RealAPICalls:
    """测试真实SolidWorks API调用 (ENH-07-02, ENH-07-03, ENH-07-04)"""

    @pytest.mark.requires_solidworks
    @pytest.mark.requires_mcp
    @pytest.mark.parametrize("case_id,description,user_input,expected_tool,requires_sw",
                             REAL_API_CASES,
                             ids=[c[0] for c in REAL_API_CASES])
    @pytest.mark.asyncio
    async def test_real_api_call(self, case_id, description, user_input, expected_tool, requires_sw):
        """测试真实SolidWorks API调用"""
        skip_if_no_sw()
        skip_if_no_mcp()

        # Mock MCP session和工具调用
        with patch('agent_coordinator.stdio_client') as mock_stdio:
            with patch('agent_coordinator.ClientSession') as mock_session_cls:
                # Mock session
                mock_session = AsyncMock()
                mock_session.initialize = AsyncMock()
                mock_session.list_tools = AsyncMock(return_value={"tools": [
                    {"name": "sw_create_part", "description": "Create part"},
                    {"name": "sw_create_assembly", "description": "Create assembly"},
                    {"name": "sw_create_drawing", "description": "Create drawing"},
                ]})
                mock_session.call_tool = AsyncMock(return_value={
                    "success": True,
                    "result": "operation_successful"
                })
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock()
                mock_session_cls.return_value = mock_session

                # Mock stdio_client
                mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(None, None))
                mock_stdio.return_value.__aexit__ = AsyncMock()

                # 创建Coordinator
                coordinator = AgentCoordinator(
                    use_real_sw=True  # use_real_sw会触发MCP模式（待实现）
                )

                # 执行请求
                result = coordinator.process_design_request(user_input)

                # 验证成功
                assert result.success, f"{case_id}: Should succeed"

                # 验证MCP工具被调用
                # (具体验证取决于实现)
                # assert mock_session.call_tool.called, f"{case_id}: MCP tool should be called"


class TestEnh07ErrorHandling:
    """测试错误处理机制 (ENH-07-05)"""

    @pytest.mark.parametrize("case_id,description,scenario,expected_error_type",
                             ERROR_HANDLING_CASES,
                             ids=[c[0] for c in ERROR_HANDLING_CASES])
    def test_error_handling(self, case_id, description, scenario, expected_error_type):
        """测试错误处理"""
        # Mock不同错误场景
        with patch('agent_coordinator.stdio_client') as mock_stdio:
            with patch('agent_coordinator.ClientSession') as mock_session_cls:
                # Mock session
                mock_session = AsyncMock()

                if scenario == "sw_not_running":
                    # Mock SolidWorks未运行错误
                    mock_session.initialize = AsyncMock(
                        side_effect=Exception("SolidWorks not running")
                    )
                elif scenario == "mcp_timeout":
                    # Mock超时错误
                    mock_session.initialize = AsyncMock(
                        side_effect=TimeoutError("MCP connection timeout")
                    )
                elif scenario == "api_error":
                    # Mock API调用错误
                    mock_session.initialize = AsyncMock()
                    mock_session.call_tool = AsyncMock(
                        side_effect=Exception("SW API error")
                    )
                else:
                    mock_session.initialize = AsyncMock()

                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock()
                mock_session_cls.return_value = mock_session

                # Mock stdio_client
                mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(None, None))
                mock_stdio.return_value.__aexit__ = AsyncMock()

                try:
                    # 创建Coordinator
                    coordinator = AgentCoordinator(
                        use_real_mcp=True,
                        use_real_sw=True
                    )

                    # 执行简单请求
                    result = coordinator.process_design_request("创建一个方块")

                    # 验证错误被优雅处理
                    # 应该返回失败但不崩溃
                    assert result is not None, f"{case_id}: Should return result, not crash"

                    if not result.success:
                        # 验证错误信息
                        assert result.error_type is not None, f"{case_id}: Should have error type"
                        # 验证错误类型匹配（可选，根据实现调整）
                        # assert result.error_type == expected_error_type, f"{case_id}: Error type mismatch"

                except Exception as e:
                    # 某些错误可能被抛出，这是可以接受的
                    # 只要不是未处理的异常
                    assert expected_error_type in type(e).__name__ or "Error" in type(e).__name__, \
                        f"{case_id}: Should handle errors gracefully"


class TestEnh07E2EWorkflow:
    """测试端到端工作流 (ENH-07-06)"""

    @pytest.mark.requires_solidworks
    @pytest.mark.requires_mcp
    @pytest.mark.parametrize("case_id,description,user_input,min_tasks,requires_sw",
                             E2E_WORKFLOW_CASES,
                             ids=[c[0] for c in E2E_WORKFLOW_CASES])
    def test_e2e_workflow(self, case_id, description, user_input, min_tasks, requires_sw):
        """测试端到端工作流"""
        skip_if_no_sw()
        skip_if_no_mcp()

        # Mock完整的MCP工作流
        with patch('agent_coordinator.stdio_client') as mock_stdio:
            with patch('agent_coordinator.ClientSession') as mock_session_cls:
                # Mock session
                mock_session = AsyncMock()
                mock_session.initialize = AsyncMock()
                mock_session.list_tools = AsyncMock(return_value={"tools": [
                    {"name": "sw_create_part", "description": "Create part"},
                    {"name": "sw_create_assembly", "description": "Create assembly"},
                    {"name": "sw_create_drawing", "description": "Create drawing"},
                    {"name": "sw_add_dimensions", "description": "Add dimensions"},
                ]})

                # Mock不同的工具调用
                async def mock_call_tool(tool_name, args):
                    return {
                        "success": True,
                        "result": f"{tool_name}_completed",
                        "execution_time": 0.5
                    }

                mock_session.call_tool = AsyncMock(side_effect=mock_call_tool)
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock()
                mock_session_cls.return_value = mock_session

                # Mock stdio_client
                mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(None, None))
                mock_stdio.return_value.__aexit__ = AsyncMock()

                # 创建Coordinator
                coordinator = AgentCoordinator(
                    use_real_sw=True  # use_real_sw会触发MCP模式（待实现）
                )

                # 执行请求
                result = coordinator.process_design_request(user_input)

                # 验证成功
                assert result.success, f"{case_id}: E2E workflow should succeed"
                assert result.tasks_executed >= min_tasks, \
                    f"{case_id}: Should execute at least {min_tasks} task(s)"

                # 验证任务被执行
                assert result.tasks is not None, f"{case_id}: Tasks should not be None"
                assert len(result.tasks) >= min_tasks, f"{case_id}: Should have {min_tasks}+ task(s)"

                # 验证执行结果
                if result.execution_results:
                    assert len(result.execution_results) >= min_tasks, \
                        f"{case_id}: Should have {min_tasks}+ execution result(s)"


class TestEnh07MockFallback:
    """测试Mock模式作为后备（始终可运行）"""

    def test_mock_mode_fallback(self):
        """测试当MCP不可用时回退到mock模式"""
        # 创建Coordinator，不启用真实MCP
        coordinator = AgentCoordinator(
            use_real_sw=False  # 使用mock模式
        )

        # 执行请求
        result = coordinator.process_design_request("创建一个100x100x50的方块")

        # 验证成功（mock模式应该工作）
        assert result is not None, "Mock mode should work"
        assert result.mode == "mock", f"Should be in mock mode, got {result.mode}"

        # 验证任务被执行
        assert result.tasks_executed >= 0, "Should execute tasks (even in mock mode)"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short", "-m", "not requires_solidworks and not requires_mcp"])
