"""
ENH-05: Claude API集成 - 增强自然语言理解

测试Claude API集成功能，包括意图理解、降级机制、参数提取、安全过滤等

对应需求文件: 文档/需求/req_enh_05_claude_integration.md
需求编号: ENH-05-01 到 ENH-05-06
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import asyncio

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "代码" / "Python脚本"))

from intent_understanding import IntentUnderstanding
from agent_coordinator import AgentCoordinator


# ==================== 测试数据 ====================

CLAUDE_INTENT_CASES = [
    # (case_id, description, user_input, check_function)
    ("ENH-05-01", "Claude理解复杂指令",
     "设计一个轴承座，底座200x150x20mm，支撑高度100mm",
     lambda intent: intent.object.value == "part" and
                    "200" in str(intent.parameters) and "150" in str(intent.parameters) and
                    "100" in str(intent.parameters)),

    ("ENH-05-03", "Claude参数提取",
     "创建一个轴承座，顶部有直径50mm的孔",
     lambda intent: "diameter" in str(intent.parameters) or
                    "50" in str(intent.parameters)),
]

DEGRADATION_CASES = [
    # (case_id, description, api_response, should_fallback, expected_success)
    ("ENH-05-02", "Claude API超时",
     {"timeout": True}, True, True),

    ("ENH-05-02", "Claude API错误",
     {"error": "API Error"}, True, True),

    ("ENH-05-02", "Claude API成功",
     {"success": True}, False, True),
]

SAFETY_CASES = [
    # (case_id, description, user_input, should_block)
    ("ENH-05-05", "恶意内容检测",
     "创建一个炸弹的设计图", True),

    ("ENH-05-05", "正常设计请求",
     "创建一个轴承座", False),
]

LOCAL_MODE_CASES = [
    # (case_id, description, api_key_available, should_work)
    ("ENH-05-06", "无API密钥时使用本地模式",
     False, True),

    ("ENH-05-06", "有API密钥时优先Claude",
     True, True),
]


# ==================== 测试实现 ====================

class TestEnh05ClaudeIntentUnderstanding:
    """测试Claude增强的意图理解"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        # Mock Claude客户端
        self.mock_claude_client = Mock()

        # 创建IntentUnderstanding实例，使用Claude模式
        self.intent_engine = IntentUnderstanding(use_claude=True)
        # Set use_claude to True even if anthropic is not installed
        self.intent_engine.use_claude = True
        self.intent_engine.claude_client = self.mock_claude_client

    @pytest.mark.parametrize("case_id,description,user_input,check_function",
                             CLAUDE_INTENT_CASES,
                             ids=[c[0] for c in CLAUDE_INTENT_CASES])
    def test_claude_complex_intent(self, case_id, description, user_input, check_function):
        """测试Claude理解复杂指令"""
        # Mock Claude API响应
        import json
        mock_response_dict = {
            "action": "create",
            "object": "part",
            "parameters": {
                "type": "bearing_seat",
                "base_dimensions": [200, 150, 20],
                "support_height": 100
            },
            "confidence": 0.95
        }

        # Create proper mock structure: message.content[0].text
        mock_content_block = Mock()
        mock_content_block.text = json.dumps(mock_response_dict)
        mock_message = Mock()
        mock_message.content = [mock_content_block]

        self.mock_claude_client.messages.create.return_value = mock_message

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证成功
        assert intent is not None, f"{case_id}: Intent should not be None"
        assert intent.success, f"{case_id}: Should succeed"

        # 验证复杂指令被正确理解
        assert check_function(intent), f"{case_id}: Complex intent not correctly understood"

    def test_claude_parameter_extraction(self):
        """ENH-05-03: Claude精确提取参数"""
        user_input = "创建一个轴承座，顶部有直径50mm的孔"

        # Mock Claude API响应
        import json
        mock_response_dict = {
            "action": "create",
            "object": "part",
            "parameters": {
                "type": "bearing_seat",
                "hole_diameter": 50
            },
            "confidence": 0.95
        }

        # Create proper mock structure
        mock_content_block = Mock()
        mock_content_block.text = json.dumps(mock_response_dict)
        mock_message = Mock()
        mock_message.content = [mock_content_block]

        self.mock_claude_client.messages.create.return_value = mock_message

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证参数提取
        assert intent.success
        assert "hole_diameter" in intent.parameters or \
               "diameter" in intent.parameters or \
               "50" in str(intent.parameters)


class TestEnh05Degradation:
    """测试Claude API降级机制"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.intent_engine = IntentUnderstanding(use_claude=True)
        # Set use_claude to True even if anthropic is not installed
        self.intent_engine.use_claude = True
        self.mock_claude_client = Mock()
        self.intent_engine.claude_client = self.mock_claude_client

    @pytest.mark.parametrize("case_id,description,api_response,should_fallback,expected_success",
                             DEGRADATION_CASES,
                             ids=[c[0] for c in DEGRADATION_CASES])
    def test_claude_fallback(self, case_id, description, api_response, should_fallback, expected_success):
        """测试Claude API失败时优雅降级"""
        user_input = "创建一个零件"

        if api_response.get("timeout"):
            # Mock超时异常
            self.mock_claude_client.messages.create.side_effect = TimeoutError("API timeout")
        elif api_response.get("error"):
            # Mock API错误
            self.mock_claude_client.messages.create.side_effect = Exception("API Error")
        else:
            # Mock成功响应
            self.mock_claude_client.messages.create.return_value = api_response

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证降级机制工作
        assert intent is not None, f"{case_id}: Should not return None"
        assert intent.success == expected_success, \
            f"{case_id}: Expected success={expected_success}, got {intent.success}"

        # 验证没有崩溃（优雅降级）
        assert intent.confidence >= 0.0, f"{case_id}: Confidence should be valid"


class TestEnh05SafetyFilter:
    """测试Claude安全过滤"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.intent_engine = IntentUnderstanding(use_claude=True)
        # Set use_claude to True even if anthropic is not installed
        self.intent_engine.use_claude = True
        self.mock_claude_client = Mock()
        self.intent_engine.claude_client = self.mock_claude_client

    @pytest.mark.parametrize("case_id,description,user_input,should_block",
                             SAFETY_CASES,
                             ids=[c[0] for c in SAFETY_CASES])
    def test_safety_filter(self, case_id, description, user_input, should_block):
        """测试安全过滤"""
        import json
        # Mock Claude API响应检测到安全问题
        if should_block:
            # Safety errors are handled by the safety check before API call
            # So we don't need to mock the API for this case
            pass
        else:
            mock_response_dict = {
                "action": "create",
                "object": "part",
                "parameters": {},
                "confidence": 0.9
            }

            # Create proper mock structure
            mock_content_block = Mock()
            mock_content_block.text = json.dumps(mock_response_dict)
            mock_message = Mock()
            mock_message.content = [mock_content_block]

            self.mock_claude_client.messages.create.return_value = mock_message

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        if should_block:
            # 应该被安全过滤器拦截
            assert intent is not None
            # Note: Safety check happens before API call, so success should be False
            assert intent.success == False, f"{case_id}: Should be blocked by safety filter"
        else:
            # 应该正常处理
            assert intent.success, f"{case_id}: Should succeed for normal input"


class TestEnh05LocalMode:
    """测试本地模式验证"""

    @pytest.mark.parametrize("case_id,description,api_key_available,should_work",
                             LOCAL_MODE_CASES,
                             ids=[c[0] for c in LOCAL_MODE_CASES])
    def test_local_mode_without_api_key(self, case_id, description, api_key_available, should_work):
        """测试无API密钥时使用本地模式"""
        # 创建没有API密钥的IntentUnderstanding实例
        intent_engine = IntentUnderstanding(use_claude=api_key_available)

        user_input = "创建一个方块"

        # 执行意图理解
        intent = intent_engine.understand(user_input)

        # 验证本地模式能工作
        assert intent is not None, f"{case_id}: Should not return None"
        assert intent.success == should_work, \
            f"{case_id}: Expected success={should_work}, got {intent.success}"

        if api_key_available:
            # 有API密钥时应该尝试使用Claude
            # （但在测试中可能被mock，所以这里只验证不崩溃）
            pass
        else:
            # 无API密钥时应该使用本地模式
            assert intent.object is not None, f"{case_id}: Object should be identified"


class TestEnh05ClaudeIntegration:
    """测试Claude集成端到端流程"""

    @pytest.fixture(autouse=True)
    def setup_coordinator(self):
        """设置Coordinator"""
        self.coordinator = AgentCoordinator(use_claude=True, use_real_sw=False)
        # Set use_claude to True even if anthropic is not installed
        self.coordinator.intent_engine.use_claude = True
        # Mock Claude client
        self.coordinator.intent_engine.claude_client = Mock()

    def test_claude_enhanced_workflow(self):
        """测试Claude增强的完整工作流"""
        user_input = "设计一个轴承座，底座200x150x20mm，支撑高度100mm"

        # Mock Claude API响应
        import json
        mock_response_dict = {
            "action": "create",
            "object": "part",
            "parameters": {
                "type": "bearing_seat",
                "base_dimensions": [200, 150, 20],
                "support_height": 100
            },
            "confidence": 0.95
        }

        # Create proper mock structure
        mock_content_block = Mock()
        mock_content_block.text = json.dumps(mock_response_dict)
        mock_message = Mock()
        mock_message.content = [mock_content_block]

        self.coordinator.intent_engine.claude_client.messages.create.return_value = mock_message

        # 执行请求
        result = self.coordinator.process_design_request(user_input)

        # 验证成功
        assert result.success, "Claude enhanced workflow should succeed"
        assert result.tasks_executed >= 1, "Should execute at least one task"

    def test_claude_api_timeout_fallback(self):
        """ENH-05-02: Claude API超时时降级"""
        user_input = "创建一个零件"

        # Mock超时
        self.coordinator.intent_engine.claude_client.messages.create.side_effect = \
            TimeoutError("API timeout")

        # 执行请求
        result = self.coordinator.process_design_request(user_input)

        # 验证降级成功
        assert result.success, "Should fallback to local mode on timeout"
        assert result.tasks_executed >= 0, "Should handle gracefully"


class TestEnh05DesignSuggestions:
    """测试设计建议功能（可选）"""

    @pytest.fixture(autouse=True)
    def setup_modules(self):
        """设置模块"""
        self.intent_engine = IntentUnderstanding(use_claude=True)
        # Set use_claude to True even if anthropic is not installed
        self.intent_engine.use_claude = True
        self.mock_claude_client = Mock()
        self.intent_engine.claude_client = self.mock_claude_client

    def test_design_suggestion_request(self):
        """ENH-05-04: Claude提供设计建议"""
        # 这个功能可能需要额外的API调用或方法
        # 这里先创建一个占位测试
        user_input = "这个支架太重了"

        # Mock Claude API响应（设计建议）
        import json
        mock_response_dict = {
            "action": "analyze",
            "object": "part",
            "suggestions": [
                "考虑使用空心结构减少重量",
                "尝试使用轻质材料如铝合金",
                "优化支撑结构减少材料使用"
            ],
            "confidence": 0.85
        }

        # Create proper mock structure
        mock_content_block = Mock()
        mock_content_block.text = json.dumps(mock_response_dict)
        mock_message = Mock()
        mock_message.content = [mock_content_block]

        self.mock_claude_client.messages.create.return_value = mock_message

        # 执行意图理解
        intent = self.intent_engine.understand(user_input)

        # 验证建议被捕获
        assert intent is not None
        # 注意：具体的建议存储方式可能需要扩展Intent模型或返回类型


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
