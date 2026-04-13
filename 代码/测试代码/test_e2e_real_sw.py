"""
E2E Integration Tests for SolidWorks Agent System

测试完整流程从用户输入到最终结果的所有模块集成
Tests the complete end-to-end flow from user input to final result

对应需求文件: 文档/需求/req_e2e.md
测试编号: E2E-01 到 E2E-10
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "代码/Python脚本"))

from agent_coordinator import AgentCoordinator, CoordinatorResult
from knowledge_base import KnowledgeBase
from intent_understanding import IntentUnderstanding
from task_decomposer import TaskDecomposer
from task_executor import TaskExecutor
from result_validator import ResultValidator
from schemas import Intent, Task, ExecutionResult, ActionType, ObjectType  # FIX-04: 添加枚举导入


# ==================== E2E 测试用例 ====================

E2E_TEST_CASES = [
    # (user_input, 预期success, 预期tasks_executed_min, 预期tasks_passed_min, 预期feedback_contains, 需求编号)
    (
        "创建一个100x100x50毫米的铝制长方体",
        True,
        1,
        1,
        ["成功", "执行"],
        "E2E-01"
    ),
    (
        "创建一个直径50mm高20mm的圆柱体",
        True,
        1,
        1,
        ["成功", "执行"],
        "E2E-02"
    ),
    (
        "创建长方体并在顶部倒角10mm",
        True,
        1,
        1,
        ["成功"],
        "E2E-03"
    ),
]

E2E_ERROR_CASES = [
    # (user_input, 预期success, 预期error_type, 预期feedback_contains, 需求编号)
    ("", False, "IntentError", ["无法"], "E2E-04"),
    ("!!###@", False, "IntentError", ["无法"], "E2E-05"),  # FIX-01: 无意义输入应返回 IntentError
]

E2E_INTEGRATION_CASES = [
    # (user_input, 预期mode, 预期success, 需求编号)
    ("创建立方体", "mock", True, "E2E-06"),
    ("Create a cube", "mock", True, "E2E-07"),
]


# ==================== E2E 测试实现 ====================

class TestE2EMockMode:
    """E2E测试 - Mock模式（不需要真实SolidWorks）"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator用于E2E测试"""
        self.coordinator = AgentCoordinator(
            use_claude=False,
            use_real_sw=False
        )

    @pytest.mark.parametrize("user_input,expected_success,min_tasks,min_passed,expected_contains,req_id", E2E_TEST_CASES)
    @pytest.mark.e2e
    def test_e2e_complete_flow(self, user_input, expected_success, min_tasks, min_passed, expected_contains, req_id):
        """测试完整流程：意图理解→任务分解→执行→验证"""
        # 执行完整流程
        result = self.coordinator.process_design_request(user_input)

        # 验证基本结构
        assert result is not None, f"{req_id}: Result should not be None"
        assert isinstance(result, CoordinatorResult), f"{req_id}: Should return CoordinatorResult"

        # 验证成功状态
        assert result.success == expected_success, f"{req_id}: Expected success={expected_success}, got {result.success}"

        # 验证执行统计
        assert result.tasks_executed >= min_tasks, f"{req_id}: Expected at least {min_tasks} tasks executed, got {result.tasks_executed}"
        assert result.tasks_passed >= min_passed, f"{req_id}: Expected at least {min_passed} tasks passed, got {result.tasks_passed}"

        # 验证反馈信息
        assert result.feedback is not None, f"{req_id}: Feedback should not be None"
        assert len(result.feedback) > 0, f"{req_id}: Feedback should not be empty"
        for expected_text in expected_contains:
            assert expected_text in result.feedback, f"{req_id}: Expected '{expected_text}' in feedback: {result.feedback}"

        # 验证模式
        assert result.mode == "mock", f"{req_id}: Expected mode='mock', got {result.mode}"

        # 验证执行时间
        assert result.total_time > 0, f"{req_id}: Total time should be positive"

        # 验证各阶段结果
        assert result.intent is not None, f"{req_id}: Intent should not be None"
        assert result.tasks is not None, f"{req_id}: Tasks should not be None"
        assert result.execution_results is not None, f"{req_id}: Execution results should not be None"

    @pytest.mark.parametrize("user_input,expected_success,expected_error,expected_contains,req_id", E2E_ERROR_CASES)
    @pytest.mark.e2e
    def test_e2e_error_handling(self, user_input, expected_success, expected_error, expected_contains, req_id):
        """测试错误处理流程"""
        result = self.coordinator.process_design_request(user_input)

        # 验证错误状态
        assert result.success == expected_success, f"{req_id}: Expected success={expected_success}"
        assert result.error_type == expected_error, f"{req_id}: Expected error_type={expected_error}, got {result.error_type}"

        # 验证错误反馈
        for expected_text in expected_contains:
            assert expected_text in result.feedback, f"{req_id}: Expected '{expected_text}' in error feedback"

    @pytest.mark.e2e
    def test_e2e_complex_workflow(self):
        """测试复杂工作流：多个连续操作"""
        # 第一步：创建基础模型
        result1 = self.coordinator.process_design_request("创建一个100x100x50毫米的长方体")
        assert result1.success, "First step should succeed"
        assert "100" in result1.feedback

        # 第二步：添加特征（在现有模型上）
        result2 = self.coordinator.process_design_request("在顶部添加10mm倒角")
        assert result2.success, "Second step should succeed"

        # 第三步：分析模型
        result3 = self.coordinator.process_design_request("分析模型质量")
        assert result3.success, "Third step should succeed"
        assert any(word in result3.feedback for word in ["质量", "mass", "kg"])

    @pytest.mark.e2e
    def test_e2e_mass_properties_analysis(self):
        """测试质量属性分析流程"""
        result = self.coordinator.process_design_request("创建一个50x50x50的钢制立方体并分析质量")

        assert result.success, "Should succeed"
        assert "立方体" in result.feedback or "cube" in result.feedback.lower()
        assert any(word in result.feedback for word in ["质量", "mass", "分析", "analysis"])


class TestE2EIntegration:
    """E2E集成测试：验证模块间交互"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator用于集成测试"""
        self.coordinator = AgentCoordinator(
            use_claude=False,
            use_real_sw=False
        )

    @pytest.mark.parametrize("user_input,expected_mode,expected_success,req_id", E2E_INTEGRATION_CASES)
    @pytest.mark.e2e
    def test_mode_selection(self, user_input, expected_mode, expected_success, req_id):
        """测试模式选择逻辑"""
        result = self.coordinator.process_design_request(user_input)

        assert result.mode == expected_mode, f"{req_id}: Expected mode={expected_mode}, got {result.mode}"
        assert result.success == expected_success, f"{req_id}: Expected success={expected_success}"

    @pytest.mark.e2e
    def test_module_integration(self):
        """测试所有模块的正确集成"""
        # 创建所有模块实例
        kb = KnowledgeBase()
        intent_engine = IntentUnderstanding(use_claude=False)  # FIX-01/02/03: 移除 knowledge_base 参数
        decomposer = TaskDecomposer()  # FIX-01/02/03: 移除 knowledge_base 参数
        executor = TaskExecutor()  # FIX-03: 移除 use_real_sw 参数

        # FIX-03: 注册 mock 工具（否则会找不到工具）
        async def mock_create_part(**kwargs):
            return {"success": True, "result": "mock_part_created", "tool_name": "create_part", "execution_time": 0.1}
        executor.register_tool("create_part", mock_create_part)
        executor.register_tool("create_sketch", mock_create_part)
        executor.register_tool("create_rectangle", mock_create_part)
        executor.register_tool("extrude_boss", mock_create_part)

        validator = ResultValidator(knowledge_base=kb)

        # 测试：意图理解
        user_input = "创建一个100x100x50毫米的长方体"
        intent = intent_engine.understand(user_input)  # FIX-04: 使用 understand 方法
        assert intent.action == ActionType.CREATE  # FIX-04: 使用 ActionType 枚举
        assert intent.object == ObjectType.PART  # FIX-04: 长方体应该是 PART 不是 FEATURE

        # 测试：任务分解
        tasks = decomposer.decompose(intent)  # FIX-03: 使用 decompose 方法
        assert len(tasks) > 0
        assert tasks[0].tool in ["create_part", "create_sketch"]  # FIX-03: 使用 tool 属性

        # 测试：任务执行
        import asyncio
        exec_result = asyncio.run(executor.execute(tasks))  # FIX-03: execute 接受任务列表
        assert exec_result is not None
        assert exec_result.success_count > 0

        # 测试：结果验证
        # FIX-03: validate 接受结果列表和意图字典
        validation = validator.validate(
            [{"success": r.success, "tool_name": r.tool_name, "result": r.result}
             for r in exec_result.results],
            {"action": intent.action.value, "object": intent.object.value}
        )
        assert validation is not None

    @pytest.mark.e2e
    def test_knowledge_base_integration(self):
        """测试知识库在流程中的集成"""
        user_input = "创建一个M10x20的螺栓"

        result = self.coordinator.process_design_request(user_input)  # FIX-05: 使用正确的方法名

        assert result.success, "Should succeed with standard fastener"
        # 知识库应该识别标准件
        assert "螺栓" in result.feedback or "bolt" in result.feedback.lower()


class TestE2EPerformance:
    """E2E性能测试"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator用于性能测试"""
        self.coordinator = AgentCoordinator(
            use_claude=False,
            use_real_sw=False
        )

    @pytest.mark.e2e
    def test_response_time(self):
        """测试响应时间（mock模式应该很快）"""
        import time

        user_input = "创建一个100x100x50毫米的长方体"

        start_time = time.time()
        result = self.coordinator.process_design_request(user_input)
        end_time = time.time()

        assert result.success, "Should succeed"
        assert result.total_time < 5.0, f"Mock mode should complete in <5s, took {end_time - start_time:.2f}s"

    @pytest.mark.e2e
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        import concurrent.futures

        requests = [
            "创建一个10x10x10的立方体",
            "创建一个20x20x20的立方体",
            "创建一个30x30x30的立方体",
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(self.coordinator.process_design_request, req) for req in requests]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # 验证所有请求都成功
        assert all(r.success for r in results), "All concurrent requests should succeed"


class TestE2EEdgeCases:
    """E2E边界情况测试"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator用于边界测试"""
        self.coordinator = AgentCoordinator(
            use_claude=False,
            use_real_sw=False
        )

    @pytest.mark.e2e
    def test_very_long_input(self):
        """测试非常长的输入"""
        long_input = "创建一个" + "非常" * 100 + "大的长方体"
        result = self.coordinator.process_design_request(long_input)

        # 应该能够处理，即使不理解
        assert result is not None
        assert isinstance(result, CoordinatorResult)

    @pytest.mark.e2e
    def test_special_characters(self):
        """测试特殊字符输入"""
        special_input = "创建一个100x100x50的长方体（铝制）"
        result = self.coordinator.process_design_request(special_input)

        assert result is not None
        assert isinstance(result, CoordinatorResult)

    @pytest.mark.e2e
    def test_mixed_language(self):
        """测试中英文混合输入"""
        mixed_input = "Create a 100x100x50mm 的 长方体"
        result = self.coordinator.process_design_request(mixed_input)

        assert result is not None
        assert isinstance(result, CoordinatorResult)
        # 应该能够处理
        if result.success:
            assert "100" in result.feedback or "100.0" in result.feedback


# ==================== 运行标记 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
