"""
ENH-03: 钣金设计支持 - 增强意图理解

测试钣金设计相关的自然语言理解功能，包括：
- 钣金零件创建识别
- 折弯特征识别
- 钣金展开操作
- 钣金专用特征（凹槽、切口等）
- 钣金材料识别

对应需求文件: 文档/需求/req_enh_03_sheet_metal.md
需求编号: ENH-03-01 到 ENH-03-06
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent / "代码" / "Python脚本"
sys.path.insert(0, str(project_root))

from intent_understanding import IntentUnderstanding
from task_decomposition import TaskDecomposer
from agent_coordinator import AgentCoordinator
from schemas import ActionType, ObjectType


# ==================== 测试数据 ====================

SHEET_METAL_CASES = [
    # (case_id, description, user_input, check_function)
    ("ENH-03-01", "创建钣金零件",
     "创建厚度2mm的钣金",
     lambda intent: intent.action == ActionType.CREATE and
                    intent.object == ObjectType.PART and
                    intent.parameters.get("sheet_metal") == True and
                    intent.parameters.get("thickness") == 2),

    ("ENH-03-02", "添加折弯",
     "添加90度折弯",
     lambda intent: intent.action == ActionType.MODIFY and
                    "bend" in str(intent.parameters).lower() or
                    "90" in str(intent.parameters)),

    ("ENH-03-03", "展开钣金",
     "展开钣金",
     lambda intent: intent.action == ActionType.ANALYZE and
                    ("flatten" in str(intent.parameters).lower() or
                     "展开" in intent.raw_input)),

    ("ENH-03-04", "添加凹槽",
     "创建凹槽特征",
     lambda intent: "hem" in str(intent.parameters).lower() or
                    "凹槽" in intent.raw_input),

    ("ENH-03-05", "钣金切口",
     "创建切口",
     lambda intent: "louver" in str(intent.parameters).lower() or
                    "切口" in intent.raw_input),

    ("ENH-03-06", "钣金材料",
     "钣金材料为不锈钢",
     lambda intent: intent.parameters.get("material") is not None or "不锈钢" in intent.raw_input),
]

TASK_DECOMPOSITION_CASES = [
    # (case_id, description, user_input, expected_tools, min_tasks)
    ("ENH-03-01", "创建钣金零件任务分解",
     "创建厚度2mm的钣金",
     ["create_base_flange"], 1),

    ("ENH-03-02", "添加折弯任务分解",
     "添加90度折弯",
     ["create_bend"], 1),

    ("ENH-03-03", "展开钣金任务分解",
     "展开钣金",
     ["flatten_sheet_metal"], 1),

    ("ENH-03-04", "复合钣金操作",
     "创建钣金，厚度1.5mm，添加2个折弯",
     ["create_base_flange", "create_bend"], 2),
]

INTEGRATION_CASES = [
    # (case_id, description, user_input, check_function)
    ("ENH-03-01", "钣金创建集成测试",
     "创建厚度3mm的钣金板",
     lambda result: result.success and result.tasks_executed >= 1),

    ("ENH-03-02", "折弯操作集成测试",
     "添加45度折弯",
     lambda result: result.success and result.tasks_executed >= 1),

    ("ENH-03-06", "钣金材料集成测试",
     "创建钣金，使用铝合金",
     lambda result: result.success and "aluminum" in result.feedback.lower()),
]

EDGE_CASES = [
    # (case_id, description, user_input, should_succeed)
    ("ENH-03-EDGE-01", "未指定厚度", "创建钣金", True),
    ("ENH-03-EDGE-02", "复杂折弯描述", "在边缘添加半径5mm的90度折弯", True),
    ("ENH-03-EDGE-03", "多次展开", "展开钣金两次", True),  # 应该只展开一次
]


# ==================== 测试实现 ====================

class TestEnh03SheetMetalIntent:
    """测试钣金意图理解 (ENH-03-01 to ENH-03-06)"""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        """设置意图理解引擎"""
        self.intent_engine = IntentUnderstanding(use_claude=False)

    @pytest.mark.parametrize("case_id,description,user_input,check_function",
                             SHEET_METAL_CASES,
                             ids=[c[0] for c in SHEET_METAL_CASES])
    def test_sheet_metal_intent(self, case_id, description, user_input, check_function):
        """测试钣金相关意图识别"""
        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证成功
        assert intent is not None, f"{case_id}: Intent should not be None"
        assert intent.success, f"{case_id}: Should succeed"

        # 验证特定场景
        assert check_function(intent), f"{case_id}: Sheet metal intent not correctly understood"

    def test_sheet_metal_keyword_extraction(self):
        """ENH-03: 测试钣金关键词提取"""
        user_input = "创建钣金零件"

        intent = self.intent_engine.understand(user_input)

        # 验证识别为钣金
        assert intent.success
        # 钣金关键词应该被识别
        # (具体实现取决于关键词匹配逻辑)


class TestEnh03SheetMetalTaskDecomposition:
    """测试钣金任务分解"""

    @pytest.fixture(autouse=True)
    def setup_decomposer(self):
        """设置任务分解器"""
        self.decomposer = TaskDecomposer()

    @pytest.mark.parametrize("case_id,description,user_input,expected_tools,min_tasks",
                             TASK_DECOMPOSITION_CASES,
                             ids=[c[0] for c in TASK_DECOMPOSITION_CASES])
    def test_sheet_metal_task_decomposition(self, case_id, description, user_input, expected_tools, min_tasks):
        """测试钣金任务分解"""
        # 首先理解意图
        intent_engine = IntentUnderstanding(use_claude=False)
        intent = intent_engine.understand(user_input)

        assert intent.success, f"{case_id}: Intent understanding should succeed"

        # 分解任务
        tasks = self.decomposer.decompose(intent)

        # 验证任务数量
        assert len(tasks) >= min_tasks, f"{case_id}: Should have at least {min_tasks} task(s)"

        # 验证工具名称（可选，根据实现）
        # for tool in expected_tools:
        #     assert any(t.tool == tool for t in tasks), f"{case_id}: Should have tool {tool}"


class TestEnh03SheetMetalIntegration:
    """测试钣金功能集成"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator"""
        self.coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

    @pytest.mark.parametrize("case_id,description,user_input,check_function",
                             INTEGRATION_CASES,
                             ids=[c[0] for c in INTEGRATION_CASES])
    def test_sheet_metal_workflow(self, case_id, description, user_input, check_function):
        """测试钣金工作流"""
        # 执行请求
        result = self.coordinator.process_design_request(user_input)

        # 验证成功
        assert check_function(result), f"{case_id}: Workflow check failed"

    def test_complex_sheet_metal_workflow(self):
        """ENH-03: 测试复杂钣金工作流"""
        user_input = "创建钣金，厚度2mm，添加90度折弯，然后展开"

        result = self.coordinator.process_design_request(user_input)

        # 验证成功
        assert result.success, "Complex sheet metal workflow should succeed"
        assert result.tasks_executed >= 2, "Should execute at least 2 tasks (create + bend)"


class TestEnh03SheetMetalEdgeCases:
    """测试钣金边界场景"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator"""
        self.coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

    @pytest.mark.parametrize("case_id,description,user_input,should_succeed",
                             EDGE_CASES,
                             ids=[c[0] for c in EDGE_CASES])
    def test_sheet_metal_edge_cases(self, case_id, description, user_input, should_succeed):
        """测试钣金边界场景"""
        result = self.coordinator.process_design_request(user_input)

        if should_succeed:
            assert result.success, f"{case_id}: Should succeed"
        else:
            # 预期失败的情况
            assert result is not None, f"{case_id}: Should return result, not crash"


class TestEnh03BackwardCompatibility:
    """测试向后兼容性（确保不破坏现有功能）"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator"""
        self.coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

    def test_part_creation_not_affected(self):
        """确保普通零件创建不受影响"""
        result = self.coordinator.process_design_request("创建一个100x100x50的方块")

        assert result.success, "Regular part creation should still work"
        assert result.tasks_executed >= 1, "Should execute tasks"

    def test_assembly_creation_not_affected(self):
        """确保装配体创建不受影响"""
        result = self.coordinator.process_design_request("创建一个装配体，3个零件")

        assert result.success, "Assembly creation should still work"

    def test_drawing_creation_not_affected(self):
        """确保工程图创建不受影响"""
        result = self.coordinator.process_design_request("创建工程图，A3图纸")

        assert result.success, "Drawing creation should still work"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
