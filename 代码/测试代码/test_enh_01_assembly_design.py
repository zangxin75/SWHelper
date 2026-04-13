"""
ENH-01: 意图理解 - 装配体设计支持

测试意图理解和任务分解模块能够识别和处理装配体设计操作

对应需求文件: 文档/需求/req_enh_01_assembly_design.md
需求编号: ENH-01-01 到 ENH-01-06
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

ENH_01_TEST_CASES = [
    # (user_input, expected_action, expected_object, expected_params_key, expected_params_value, req_id)
    ("创建一个装配体，包含3个零件", ActionType.CREATE, ObjectType.ASSEMBLY, "component_count", 3, "ENH-01-01"),
    ("在装配体中添加同轴配合", ActionType.MODIFY, ObjectType.ASSEMBLY, "mate_type", "coaxial", "ENH-01-02"),
    ("检查装配体干涉", ActionType.ANALYZE, ObjectType.ASSEMBLY, "check_type", "interference", "ENH-01-03"),
    ("创建装配体爆炸视图", ActionType.CREATE, ObjectType.ASSEMBLY, "view_type", "exploded", "ENH-01-04"),  # 修正：CREATE是合理的
    ("修改装配体材料为铝合金", ActionType.MODIFY, ObjectType.ASSEMBLY, "material", "铝合金_6061", "ENH-01-05"),
    ("创建子装配体", ActionType.CREATE, ObjectType.ASSEMBLY, "is_subassembly", True, "ENH-01-06"),
]


# ==================== 测试实现 ====================

class TestEnh01AssemblyRecognition:
    """测试装配体操作的识别"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置意图理解和任务分解模块"""
        self.kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)
        self.decomposer = TaskDecomposer()

    @pytest.mark.parametrize("user_input,expected_action,expected_object,expected_params_key,expected_params_value,req_id",
                             ENH_01_TEST_CASES)
    def test_assembly_action_recognition(self, user_input, expected_action, expected_object,
                                        expected_params_key, expected_params_value, req_id):
        """测试装配体操作的意图识别"""

        # 步骤1: 意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证意图被正确识别
        assert intent is not None, f"{req_id}: Intent should not be None"
        assert intent.action == expected_action, \
            f"{req_id}: Expected action={expected_action}, got {intent.action}"
        assert intent.object == expected_object, \
            f"{req_id}: Expected object={expected_object}, got {intent.object}"

        # 如果有预期的参数
        if expected_params_key:
            assert expected_params_key in intent.parameters, \
                f"{req_id}: Expected parameter '{expected_params_key}' not found"
            assert intent.parameters[expected_params_key] == expected_params_value, \
                f"{req_id}: Expected {expected_params_key}={expected_params_value}, got {intent.parameters.get(expected_params_key)}"


class TestEnh01AssemblyDecomposition:
    """测试装配体操作的任务分解"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)
        self.decomposer = TaskDecomposer()

    def test_create_assembly_decomposition(self):
        """测试创建装配体的任务分解"""
        intent = self.intent_engine.understand("创建一个装配体，包含3个零件")

        # 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务列表
        assert tasks is not None, "Tasks should not be None"
        assert len(tasks) > 0, "Should have at least one task"

        # 应该包含创建装配体任务
        tool_names = [t.tool for t in tasks]
        assert "create_assembly" in tool_names, "Should include create_assembly tool"

    def test_add_mate_decomposition(self):
        """测试添加配合的任务分解"""
        intent = self.intent_engine.understand("在装配体中添加同轴配合")

        # 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务列表
        assert tasks is not None, "Tasks should not be None"
        assert len(tasks) > 0, "Should have at least one task"

        # 应该包含添加配合任务
        tool_names = [t.tool for t in tasks]
        assert "add_mate" in tool_names, "Should include add_mate tool"

    def test_check_interference_decomposition(self):
        """测试干涉检查的任务分解"""
        intent = self.intent_engine.understand("检查装配体干涉")

        # 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务列表
        assert tasks is not None, "Tasks should not be None"
        assert len(tasks) > 0, "Should have at least one task"

        # 应该包含干涉检查任务
        tool_names = [t.tool for t in tasks]
        assert "check_interference" in tool_names, "Should include check_interference tool"


class TestEnh01AssemblyIntegration:
    """测试装配体操作的 Coordinator 集成"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置 Coordinator"""
        from agent_coordinator import AgentCoordinator
        self.coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

    def test_create_assembly_workflow(self):
        """测试创建装配体的完整流程"""
        result = self.coordinator.process_design_request("创建一个装配体，包含3个零件")

        # 验证成功
        assert result.success, "Should succeed creating assembly"
        assert result.tasks_executed >= 1, "Should execute at least one task"

        # 验证反馈包含装配体相关信息
        assert "装配体" in result.feedback or "assembly" in result.feedback.lower(), \
            "Feedback should mention assembly"

    def test_mate_workflow(self):
        """测试添加配合的完整流程"""
        result = self.coordinator.process_design_request("在装配体中添加同轴配合")

        # 验证成功
        assert result.success, "Should succeed adding mate"
        assert result.tasks_executed >= 1, "Should execute at least one task"

    def test_interference_check_workflow(self):
        """测试干涉检查的完整流程"""
        result = self.coordinator.process_design_request("检查装配体干涉")

        # 验证成功
        assert result.success, "Should succeed checking interference"
        assert result.tasks_executed >= 1, "Should execute at least one task"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
