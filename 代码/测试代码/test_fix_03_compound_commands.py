"""
FIX-03: 任务分解 - 支持复合指令（创建+分析）

测试任务分解模块能够识别复合操作指令

对应需求文件: 文档/需求/req_phase2_fixes_and_enhancements.md
需求编号: FIX-03
测试用例: FIX-03-01 到 FIX-03-06
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "代码/Python脚本"))

from intent_understanding import IntentUnderstanding
from task_decomposition import TaskDecomposer
from knowledge_base import KnowledgeBase
from schemas import ActionType, ObjectType


# ==================== 测试用例数据 ====================

FIX_03_TEST_CASES = [
    # (user_input, expected_tools, req_id)
    ("创建方块并分析质量", ["create_part", "calculate_mass"], "FIX-03-01"),
    ("创建圆柱并导出STEP", ["create_part", "export_step"], "FIX-03-02"),
    ("创建零件，材料为铝合金", ["create_part", "assign_material"], "FIX-03-03"),
    ("创建方块，分析质量，导出PDF", ["create_part", "calculate_mass", "export_pdf"], "FIX-03-04"),
    ("创建方块分析质量", ["create_part", "calculate_mass"], "FIX-03-05"),  # 无连接词
    ("创建方块", ["create_part"], "FIX-03-06"),  # 单一操作
]


# ==================== 测试实现 ====================

class TestFix03CompoundCommands:
    """测试复合指令的识别和分解"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置意图理解和任务分解模块"""
        self.kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(knowledge_base=self.kb)
        self.decomposer = TaskDecomposer(knowledge_base=self.kb)

    @pytest.mark.parametrize("user_input,expected_tools,req_id", FIX_03_TEST_CASES)
    def test_compound_command_decomposition(self, user_input, expected_tools, req_id):
        """测试复合指令的任务分解"""

        # 步骤1: 意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证意图
        assert intent is not None, f"{req_id}: Intent should not be None"
        assert intent.action == ActionType.CREATE, f"{req_id}: Expected CREATE action"

        # 步骤2: 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务数量
        assert len(tasks) == len(expected_tools), \
            f"{req_id}: Expected {len(expected_tools)} tasks, got {len(tasks)}"

        # 验证每个预期的工具都存在
        actual_tools = [task.tool_name for task in tasks]
        for expected_tool in expected_tools:
            assert expected_tool in actual_tools, \
                f"{req_id}: Expected tool '{expected_tool}' not found in {actual_tools}"

    @pytest.mark.parametrize("user_input,expected_tools,req_id", FIX_03_TEST_CASES)
    def test_coordinator_compound_execution(self, user_input, expected_tools, req_id):
        """测试Coordinator执行复合指令"""

        from agent_coordinator import AgentCoordinator

        coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

        # 执行复合指令
        result = coordinator.process_design_request(user_input)

        # 验证结果
        assert result.success, f"{req_id}: Compound command should succeed for '{user_input}'"
        assert result.tasks_executed == len(expected_tools), \
            f"{req_id}: Expected {len(expected_tools)} tasks executed, got {result.tasks_executed}"
        assert result.tasks_passed >= len(expected_tools) - 1, \
            f"{req_id}: Expected at least {len(expected_tools) - 1} tasks passed"

        # 验证反馈信息
        assert "成功" in result.feedback or "执行" in result.feedback, \
            f"{req_id}: Feedback should indicate success"

    def test_mass_properties_analysis_integration(self):
        """测试E2E-09: 创建并分析质量"""
        coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

        result = coordinator.process_design_request("创建一个50x50x50的钢制立方体并分析质量")

        # 验证成功
        assert result.success, "Should succeed creating cube and analyzing mass"

        # 验证包含创建和分析操作
        assert result.tasks_executed >= 2, "Should execute at least 2 tasks (create + analyze)"

        # 验证反馈包含质量相关信息
        assert any(word in result.feedback for word in ["质量", "mass", "分析", "analysis"]), \
            "Feedback should mention mass analysis"


class TestFix03CompoundPatterns:
    """测试复合指令的模式"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(knowledge_base=self.kb)
        self.decomposer = TaskDecomposer(knowledge_base=self.kb)

    def test_connector_variations(self):
        """测试不同的连接词"""
        test_cases = [
            "创建方块并分析质量",  # 并
            "创建方块，分析质量",   # 逗号
            "创建方块然后分析质量", # 然后
            "创建方块分析质量",     # 无连接词
        ]

        for user_input in test_cases:
            intent = self.intent_engine.understand(user_input)
            tasks = self.decomposer.decompose(intent)

            # 所有情况都应该生成2个任务
            assert len(tasks) >= 2, f"Should have at least 2 tasks for '{user_input}', got {len(tasks)}"

            # 应该包含创建和分析工具
            tool_names = [t.tool_name for t in tasks]
            assert "create_part" in tool_names, f"Should include create_part for '{user_input}'"
            assert "calculate_mass" in tool_names, f"Should include calculate_mass for '{user_input}'"

    def test_three_part_compound(self):
        """测试三部分复合指令"""
        intent = self.intent_engine.understand("创建方块，分析质量，导出PDF")
        tasks = self.decomposer.decompose(intent)

        # 应该生成3个任务
        assert len(tasks) == 3, "Should have exactly 3 tasks"

        # 验证工具名称
        tool_names = [t.tool_name for t in tasks]
        assert "create_part" in tool_names
        assert "calculate_mass" in tool_names
        assert "export_pdf" in tool_names

    def test_compound_with_material(self):
        """测试包含材料的复合指令"""
        intent = self.intent_engine.understand("创建零件，材料为铝合金")
        tasks = self.decomposer.decompose(intent)

        # 应该生成2个任务：创建和设置材料
        assert len(tasks) >= 2, "Should have at least 2 tasks"

        tool_names = [t.tool_name for t in tasks]
        assert "create_part" in tool_names
        assert "assign_material" in tool_names

        # 验证材料参数
        material_task = next((t for t in tasks if t.tool_name == "assign_material"), None)
        assert material_task is not None, "Should have assign_material task"
        assert "material" in material_task.parameters, "Should have material parameter"
        assert "铝" in material_task.parameters["material"], "Material should contain '铝'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
