"""
FIX-01: 意图理解 - 拒绝非结构化输入

测试意图理解模块能够正确识别并拒绝无法解析的输入

对应需求文件: 文档/需求/req_phase2_fixes_and_enhancements.md
需求编号: FIX-01
测试用例: FIX-01-01 到 FIX-01-06
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

FIX_01_TEST_CASES = [
    # (user_input, expected_success, expected_error_type, expected_feedback_contains, expected_action, req_id)
    ("", False, "IntentError", "无法理解", None, "FIX-01-01"),
    ("!!###@", False, "IntentError", "无法理解", None, "FIX-01-02"),
    ("。。。？？？", False, "IntentError", "无法理解", None, "FIX-01-03"),
    ("asdfgh", False, "IntentError", "无法理解", None, "FIX-01-04"),
    ("创", False, "IntentError", "信息不足", None, "FIX-01-05"),
    ("创建方块", True, None, None, ActionType.CREATE, "FIX-01-06"),  # 正常输入应成功
]


# ==================== 测试实现 ====================

class TestFix01IntentRejection:
    """测试意图理解模块的输入拒绝机制"""

    @pytest.fixture(autouse=True)
    def setup_intent_engine(self):
        """设置意图理解引擎"""
        kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)

    @pytest.mark.parametrize("user_input,expected_success,expected_error_type,expected_feedback_contains,expected_action,req_id",
                             FIX_01_TEST_CASES)
    def test_intent_understanding_rejection(self, user_input, expected_success, expected_error_type,
                                           expected_feedback_contains, expected_action, req_id):
        """测试意图理解对各种输入的处理"""

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证结果
        assert intent is not None, f"{req_id}: Intent should not be None"

        # 验证成功/失败状态
        if expected_success:
            # 预期成功的情况
            assert intent.action == expected_action, f"{req_id}: Expected action={expected_action}, got {intent.action}"
            assert intent.confidence > 0.5, f"{req_id}: Confidence should be > 0.5 for valid input"
        else:
            # 预期失败的情况
            # 意图理解可能返回一个"未知"意图，而不是抛出异常
            # 我们检查置信度是否很低
            assert intent.confidence < 0.5, f"{req_id}: Expected low confidence for unparseable input, got {intent.confidence}"

            # 或者检查是否返回了特定的错误动作
            # 如果意图理解引擎实现中返回了UNKNOWN动作
            if intent.action == ActionType.UNKNOWN:
                pass  # 这是可以接受的行为
            else:
                # 如果不是UNKNOWN，那么置信度应该非常低
                assert intent.confidence < 0.3, f"{req_id}: Expected very low confidence for unparseable input"

    @pytest.mark.parametrize("user_input,expected_success,expected_error_type,expected_feedback_contains,expected_action,req_id",
                             FIX_01_TEST_CASES)
    def test_coordinator_integration(self, user_input, expected_success, expected_error_type,
                                     expected_feedback_contains, expected_action, req_id):
        """测试在Coordinator层面的集成行为"""

        from agent_coordinator import AgentCoordinator

        coordinator = AgentCoordinator(use_claude=False, use_real_sw=False)

        # 执行完整流程
        result = coordinator.process_design_request(user_input)

        # 验证结果
        if expected_success:
            # 正常输入应该成功
            assert result.success, f"{req_id}: Expected success=True for valid input '{user_input}'"
            assert result.error_type is None, f"{req_id}: Should not have error_type for valid input"
        else:
            # 无效输入应该失败
            assert not result.success, f"{req_id}: Expected success=False for invalid input '{user_input}'"
            assert result.error_type is not None, f"{req_id}: Should have error_type for invalid input"

            # 验证错误类型
            if expected_error_type:
                assert result.error_type == expected_error_type, f"{req_id}: Expected error_type={expected_error_type}, got {result.error_type}"

            # 验证反馈信息
            if expected_feedback_contains:
                assert expected_feedback_contains in result.feedback, \
                    f"{req_id}: Expected '{expected_feedback_contains}' in feedback, got: {result.feedback}"


class TestFix01EdgeCases:
    """测试额外的边界情况"""

    @pytest.fixture(autouse=True)
    def setup_intent_engine(self):
        """设置意图理解引擎"""
        kb = KnowledgeBase()
        self.intent_engine = IntentUnderstanding(use_claude=False)

    def test_whitespace_only(self):
        """测试纯空格输入"""
        intent = self.intent_engine.understand("   ")
        assert intent.confidence < 0.5, "Whitespace-only input should have low confidence"

    def test_newlines_only(self):
        """测试纯换行输入"""
        intent = self.intent_engine.understand("\n\n\n")
        assert intent.confidence < 0.5, "Newline-only input should have low confidence"

    def test_mixed_invalid_chars(self):
        """测试混合无效字符"""
        intent = self.intent_engine.understand("@#$%^&*()")
        assert intent.confidence < 0.5, "Mixed special chars should have low confidence"

    def test_very_long_invalid_input(self):
        """测试超长无效输入"""
        long_invalid = "asdfgh" * 1000
        intent = self.intent_engine.understand(long_invalid)
        assert intent.confidence < 0.5, "Long invalid input should have low confidence"

    def test_numbers_only(self):
        """测试纯数字输入"""
        intent = self.intent_engine.understand("12345")
        assert intent.confidence < 0.5, "Numbers-only input should have low confidence"

    def test_english_gibberish(self):
        """测试英文乱码"""
        intent = self.intent_engine.understand("qwertyuiop")
        assert intent.confidence < 0.5, "English gibberish should have low confidence"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
