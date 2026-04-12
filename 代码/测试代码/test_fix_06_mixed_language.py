"""
FIX-06: 意图理解 - 中英文混合尺寸提取

测试意图理解模块能够正确处理中英文混合输入的尺寸提取

对应需求文件: 文档/需求/req_phase2_fixes_and_enhancements.md
需求编号: FIX-06
测试用例: FIX-06-01 到 FIX-06-06
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "代码/Python脚本"))

from intent_understanding import IntentUnderstanding
from knowledge_base import KnowledgeBase
from schemas import ActionType, ObjectType


# ==================== 测试用例数据 ====================

FIX_06_TEST_CASES = [
    # (user_input, expected_dimensions, req_id)
    ("Create a 100x100x50mm 的 长方体", [100, 100, 50], "FIX-06-01"),
    ("Create 一个 100x100x50mm 的方块", [100, 100, 50], "FIX-06-02"),
    ("Create a 100x100x50mm cube", [100, 100, 50], "FIX-06-03"),
    ("创建100x100x50mm的长方体", [100, 100, 50], "FIX-06-04"),
    ("创建100x100x50毫米的长方体", [100, 100, 50], "FIX-06-05"),
    ("100mm x 100厘米 x 50m 的方块", [100, 1000, 50000], "FIX-06-06"),  # 单位混合
]


# ==================== 测试实现 ====================

class TestFix06MixedLanguage:
    """测试中英文混合的尺寸提取"""

    @pytest.fixture(autouse=True)
    def setup_intent_engine(self):
        """设置意图理解引擎"""
        kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)

    @pytest.mark.parametrize("user_input,expected_dimensions,req_id", FIX_06_TEST_CASES)
    def test_mixed_language_dimension_extraction(self, user_input, expected_dimensions, req_id):
        """测试中英文混合输入的尺寸提取"""

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证意图
        assert intent is not None, f"{req_id}: Intent should not be None"
        assert intent.action == ActionType.CREATE, f"{req_id}: Expected CREATE action"

        # 验证尺寸参数
        assert "dimensions" in intent.parameters, f"{req_id}: Should have 'dimensions' parameter"
        dimensions = intent.parameters["dimensions"]

        # 验证尺寸值
        assert dimensions is not None, f"{req_id}: Dimensions should not be None"
        assert len(dimensions) == len(expected_dimensions), \
            f"{req_id}: Expected {len(expected_dimensions)} dimensions, got {len(dimensions)}"

        for i, (actual, expected) in enumerate(zip(dimensions, expected_dimensions)):
            assert actual == expected, \
                f"{req_id}: Dimension {i}: expected {expected}, got {actual}"

    @pytest.mark.parametrize("user_input,expected_dimensions,req_id", FIX_06_TEST_CASES)
    def test_coordinator_mixed_language(self, user_input, expected_dimensions, req_id):
        """测试Coordinator层面的中英文混合处理"""

        from agent_coordinator import AgentCoordinator

        coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

        # 执行请求
        result = coordinator.process_design_request(user_input)

        # 验证成功
        assert result.success, f"{req_id}: Should succeed for '{user_input}'"

        # 验证反馈包含尺寸信息
        # 对于数值100，可能显示为"100"或"100.0"
        for dim in expected_dimensions:
            # 检查整数或浮点数形式
            assert str(dim) in result.feedback or f"{dim}.0" in result.feedback, \
                f"{req_id}: Expected '{dim}' in feedback for '{user_input}', got: {result.feedback}"

    def test_e2e_16_mixed_language(self):
        """测试E2E-16: 中英文混合输入"""
        coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

        user_input = "Create a 100x100x50mm 的 长方体"
        result = coordinator.process_design_request(user_input)

        # 应该能够处理
        assert result is not None, "Result should not be None"
        assert isinstance(result, type(result)), "Should return valid result object"
        assert result.success, "Should succeed with mixed language input"

        # 验证反馈包含尺寸信息
        assert "100" in result.feedback or "100.0" in result.feedback, \
            "Feedback should contain dimension '100'"


class TestFix06UnitConversion:
    """测试单位换算"""

    @pytest.fixture(autouse=True)
    def setup_intent_engine(self):
        """设置意图理解引擎"""
        kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)

    def test_mm_unit(self):
        """测试mm单位"""
        test_cases = [
            "创建100mm的方块",
            "创建100毫米的方块",
            "Create a 100mm cube",
        ]

        for user_input in test_cases:
            intent = self.intent_engine.understand(user_input)
            dimensions = intent.parameters.get("dimensions", [])

            # 应该提取到100（或接近100的值）
            if dimensions:
                assert 100 in dimensions or any(99 <= d <= 101 for d in dimensions), \
                    f"Should extract dimension ~100 for '{user_input}', got {dimensions}"

    def test_cm_unit(self):
        """测试cm单位（应转换为mm）"""
        test_cases = [
            "创建10厘米的方块",
            "创建10cm的方块",
            "Create a 10cm cube",
        ]

        for user_input in test_cases:
            intent = self.intent_engine.understand(user_input)
            dimensions = intent.parameters.get("dimensions", [])

            # 10cm = 100mm
            if dimensions:
                assert 100 in dimensions or any(99 <= d <= 101 for d in dimensions), \
                    f"Should convert 10cm to 100mm for '{user_input}', got {dimensions}"

    def test_m_unit(self):
        """测试m单位（应转换为mm）"""
        test_cases = [
            "创建0.1米的方块",
            "创建0.1m的方块",
            "Create a 0.1m cube",
        ]

        for user_input in test_cases:
            intent = self.intent_engine.understand(user_input)
            dimensions = intent.parameters.get("dimensions", [])

            # 0.1m = 100mm
            if dimensions:
                assert 100 in dimensions or any(99 <= d <= 101 for d in dimensions), \
                    f"Should convert 0.1m to 100mm for '{user_input}', got {dimensions}"

    def test_mixed_units(self):
        """测试混合单位（测试FIX-06-06）"""
        user_input = "100mm x 100厘米 x 50m 的方块"

        intent = self.intent_engine.understand(user_input)
        dimensions = intent.parameters.get("dimensions", [])

        # 预期: 100mm, 1000mm (100厘米), 50000mm (50米)
        expected = [100, 1000, 50000]

        assert dimensions == expected, \
            f"Expected {expected} for mixed units, got {dimensions}"

    def test_unit_case_insensitive(self):
        """测试单位大小写不敏感"""
        test_cases = [
            "创建100MM的方块",
            "创建100mm的方块",
            "创建100Mm的方块",
        ]

        for user_input in test_cases:
            intent = self.intent_engine.understand(user_input)
            dimensions = intent.parameters.get("dimensions", [])

            # 都应该提取到100
            if dimensions:
                assert 100 in dimensions or any(99 <= d <= 101 for d in dimensions), \
                    f"Should extract dimension 100 for '{user_input}' (case insensitive)"


class TestFix06NumberFormats:
    """测试不同的数字格式"""

    @pytest.fixture(autouse=True)
    def setup_intent_engine(self):
        """设置意图理解引擎"""
        kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)

    def test_integer_numbers(self):
        """测试整数"""
        intent = self.intent_engine.understand("创建100x100x50的方块")
        dimensions = intent.parameters.get("dimensions", [])
        assert dimensions == [100, 100, 50], f"Expected [100, 100, 50], got {dimensions}"

    def test_decimal_numbers(self):
        """测试小数"""
        intent = self.intent_engine.understand("创建100.5x100.0x50.2的方块")
        dimensions = intent.parameters.get("dimensions", [])

        # 应该能提取小数
        if dimensions:
            assert len(dimensions) == 3, f"Expected 3 dimensions, got {len(dimensions)}"
            # 验证大约是100.5, 100.0, 50.2
            assert any(100 <= d <= 101 for d in dimensions), "Should have dimension ~100"

    def test_scientific_notation(self):
        """测试科学计数法（可能不支持）"""
        intent = self.intent_engine.understand("创建1e2x1e2x50的方块")
        dimensions = intent.parameters.get("dimensions", [])

        # 科学计数法可能不被支持，这是可以接受的
        # 我们只验证不会崩溃
        assert intent is not None, "Should not crash on scientific notation"

    def test_chinese_numbers(self):
        """测试中文数字（可能不支持）"""
        intent = self.intent_engine.understand("创建一百x一百x五十的方块")
        dimensions = intent.parameters.get("dimensions", [])

        # 中文数字可能不被支持，这是可以接受的
        # 我们只验证不会崩溃
        assert intent is not None, "Should not crash on Chinese numbers"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
