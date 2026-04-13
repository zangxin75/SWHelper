"""
ENH-02: 意图理解 - 工程图创建支持

测试意图理解和任务分解模块能够识别和处理工程图设计操作

对应需求文件: 文档/需求/req_enh_02_drawing_creation.md
需求编号: ENH-02-01 到 ENH-02-06
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

ENH_02_TEST_CASES = [
    # (user_input, expected_action, expected_object, expected_params_key, expected_params_value, req_id)
    ("创建工程图，3个视图", ActionType.CREATE, ObjectType.DRAWING, "view_count", 3, "ENH-02-01"),
    ("添加所有尺寸", ActionType.MODIFY, ObjectType.DRAWING, "annotation", "dimensions", "ENH-02-02"),
    ("添加技术要求注释", ActionType.MODIFY, ObjectType.DRAWING, "annotation", "note", "ENH-02-03"),
    ("导出工程图为PDF", ActionType.EXPORT, ObjectType.DRAWING, "format", "pdf", "ENH-02-04"),
    ("使用A3图纸", None, ObjectType.DRAWING, "sheet_format", "A3", "ENH-02-05"),
    ("比例1:2", None, ObjectType.DRAWING, "scale", "1:2", "ENH-02-06"),
]

SHEET_FORMAT_CASES = [
    ("创建A0图纸", "sheet_format", "A0"),
    ("使用A1格式", "sheet_format", "A1"),
    ("A2图纸", "sheet_format", "A2"),
    ("A3格式", "sheet_format", "A3"),
    ("使用A4", "sheet_format", "A4"),
]

SCALE_CASES = [
    ("1:1", "比例1:1", "1:1"),
    ("1:2", "比例1:2", "1:2"),
    ("2:1", "放大2倍", "2:1"),
    ("1:5", "1:5比例", "1:5"),
    ("1:10", "比例1:10", "1:10"),
]


# ==================== 测试实现 ====================

class TestEnh02DrawingRecognition:
    """测试工程图操作的识别"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置意图理解和任务分解模块"""
        self.kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)
        self.decomposer = TaskDecomposer()

    @pytest.mark.parametrize("user_input,expected_action,expected_object,expected_params_key,expected_params_value,req_id",
                             ENH_02_TEST_CASES)
    def test_drawing_object_recognition(self, user_input, expected_action, expected_object,
                                       expected_params_key, expected_params_value, req_id):
        """测试工程图操作的意图识别"""

        # 步骤1: 意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证意图被正确识别
        assert intent is not None, f"{req_id}: Intent should not be None"
        assert intent.object == expected_object, \
            f"{req_id}: Expected object={expected_object}, got {intent.object}"

        # 如果有预期的action
        if expected_action:
            assert intent.action == expected_action, \
                f"{req_id}: Expected action={expected_action}, got {intent.action}"

        # 如果有预期的参数
        if expected_params_key:
            assert expected_params_key in intent.parameters, \
                f"{req_id}: Expected parameter '{expected_params_key}' not found"
            assert intent.parameters[expected_params_key] == expected_params_value, \
                f"{req_id}: Expected {expected_params_key}={expected_params_value}, got {intent.parameters.get(expected_params_key)}"


class TestEnh02SheetFormatRecognition:
    """测试图纸格式识别"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.intent_engine = IntentUnderstanding(use_claude=False)

    @pytest.mark.parametrize("input_text,param_key,expected_value", SHEET_FORMAT_CASES)
    def test_sheet_format_recognition(self, input_text, param_key, expected_value):
        """测试各种图纸格式识别"""
        intent = self.intent_engine.understand(input_text)

        assert intent is not None
        assert intent.object == ObjectType.DRAWING
        assert param_key in intent.parameters
        assert intent.parameters[param_key] == expected_value


class TestEnh02ScaleRecognition:
    """测试比例识别"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.intent_engine = IntentUnderstanding(use_claude=False)

    @pytest.mark.parametrize("scale_str,input_text,expected_scale", SCALE_CASES)
    def test_scale_recognition(self, scale_str, input_text, expected_scale):
        """测试各种比例识别"""
        intent = self.intent_engine.understand(input_text)

        assert intent is not None
        assert "scale" in intent.parameters
        assert intent.parameters["scale"] == expected_scale


class TestEnh02DrawingDecomposition:
    """测试工程图任务分解"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)
        self.decomposer = TaskDecomposer()

    def test_create_drawing_decomposition(self):
        """测试创建工程图任务分解"""
        intent = self.intent_engine.understand("创建工程图，3个视图")

        # 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务列表
        assert tasks is not None
        assert len(tasks) > 0

        # 应该包含创建工程图任务
        tool_names = [t.tool for t in tasks]
        assert "create_drawing" in tool_names

    def test_add_dimensions_decomposition(self):
        """测试添加尺寸任务分解"""
        intent = self.intent_engine.understand("添加所有尺寸")

        # 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务列表
        assert tasks is not None
        assert len(tasks) > 0

        # 应该包含添加尺寸任务
        tool_names = [t.tool for t in tasks]
        assert "add_dimensions" in tool_names

    def test_export_pdf_decomposition(self):
        """测试导出PDF任务分解"""
        intent = self.intent_engine.understand("导出工程图为PDF")

        # 任务分解
        tasks = self.decomposer.decompose(intent)

        # 验证任务列表
        assert tasks is not None
        assert len(tasks) > 0

        # 应该包含导出PDF任务
        tool_names = [t.tool for t in tasks]
        assert "export_drawing_pdf" in tool_names or "export_pdf" in tool_names


class TestEnh02DrawingIntegration:
    """测试工程图集成流程"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置 Coordinator"""
        from agent_coordinator import AgentCoordinator
        self.coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

    def test_create_drawing_workflow(self):
        """测试创建工程图完整流程"""
        result = self.coordinator.process_design_request("创建工程图，3个视图，A3图纸")

        # 验证成功
        assert result.success
        assert result.tasks_executed >= 1

    def test_add_dimensions_workflow(self):
        """测试添加尺寸流程"""
        result = self.coordinator.process_design_request("添加所有尺寸")

        # 验证成功
        assert result.success
        assert result.tasks_executed >= 1

    def test_export_pdf_workflow(self):
        """测试导出PDF流程"""
        result = self.coordinator.process_design_request("导出工程图为PDF")

        # 验证成功
        assert result.success
        assert result.tasks_executed >= 1


class TestEnh02DrawingEdgeCases:
    """测试工程图边界场景"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.intent_engine = IntentUnderstanding(use_claude=False)

    def test_invalid_sheet_format(self):
        """测试无效的图纸格式"""
        intent = self.intent_engine.understand("使用B5图纸")

        # 应该识别为DRAWING，但格式可能不是标准值
        assert intent is not None
        assert intent.object == ObjectType.DRAWING

    def test_complex_scale(self):
        """测试复杂比例"""
        intent = self.intent_engine.understand("比例1:2.5")

        assert intent is not None
        assert "scale" in intent.parameters

    def test_combined_parameters(self):
        """测试组合参数"""
        intent = self.intent_engine.understand("创建A3工程图，比例1:2，包含3个视图")

        assert intent is not None
        assert intent.object == ObjectType.DRAWING
        # 至少应该识别出一些参数
        assert len(intent.parameters) > 0


class TestEnh02DrawingE2E:
    """E2E测试：工程图完整场景"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置 Coordinator"""
        from agent_coordinator import AgentCoordinator
        self.coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

    @pytest.mark.e2e
    def test_e2e_21_create_drawing_with_views(self):
        """E2E-21: 创建包含多个视图的工程图"""
        result = self.coordinator.process_design_request(
            "创建一个工程图，包含前视、俯视、左视三个视图"
        )

        assert result.success
        assert result.tasks_executed >= 1

    @pytest.mark.e2e
    def test_e2e_22_drawing_with_dimensions(self):
        """E2E-22: 创建工程图并添加尺寸"""
        result = self.coordinator.process_design_request(
            "创建工程图并添加所有尺寸标注"
        )

        assert result.success
        assert result.tasks_executed >= 2  # 创建+标注

    @pytest.mark.e2e
    def test_e2e_23_drawing_export_pdf(self):
        """E2E-23: 创建工程图并导出PDF"""
        result = self.coordinator.process_design_request(
            "创建A3工程图并导出为PDF文件"
        )

        assert result.success
        assert "pdf" in result.feedback.lower() or result.tasks_executed >= 2

    @pytest.mark.e2e
    def test_e2e_24_complete_drawing_workflow(self):
        """E2E-24: 完整工程图工作流（创建+标注+导出）"""
        result = self.coordinator.process_design_request(
            "创建A3工程图，3个视图，添加尺寸和注释，导出PDF"
        )

        assert result.success
        assert result.tasks_executed >= 3  # 至少3个步骤


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
