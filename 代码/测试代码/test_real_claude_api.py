"""
测试真实Claude API集成

用途: 验证Claude API在真实场景下的表现
前提: 需要Anthropic API密钥

配置方式:
1. 环境变量 (推荐):
   export ANTHROPIC_API_KEY="your-api-key-here"

2. 直接传入 (临时测试):
   api_key="sk-ant-..."

运行方式:
    python test_real_claude_api.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent / "代码" / "Python脚本"
sys.path.insert(0, str(project_root))

from intent_understanding import IntentUnderstanding


# ==================== 测试用例 ====================

TEST_CASES = [
    # (case_id, description, user_input, 预期要点)
    ("COMPLEX-01", "复杂零件设计",
     "设计一个轴承座，底座200x150x20mm，支撑高度100mm，顶部有直径50mm的孔，使用45号钢",
     ["应该识别: action=create, object=part",
      "应该提取: base_dimensions=[200,150,20]",
      "应该提取: support_height=100",
      "应该提取: hole_diameter=50",
      "应该提取: material=45号钢",
      "confidence应该>0.9"]),

    ("COMPLEX-02", "工程图创建",
     "创建一个工程图，使用A3图纸，1:2比例，包含3个视图",
     ["应该识别: action=create, object=drawing",
      "应该提取: sheet_format=A3",
      "应该提取: scale=1:2",
      "应该提取: view_count=3",
      "confidence应该>0.9"]),

    ("COMPLEX-03", "装配体设计",
     "创建一个装配体，包含5个零件，使用同轴配合，检查干涉",
     ["应该识别: action=create, object=assembly",
      "应该提取: component_count=5",
      "应该提取: mate_type=同轴",
      "应该提取: check_type=干涉",
      "confidence应该>0.9"]),

    ("MODIFY-01", "修改操作",
     "修改这个零件，把高度从100mm改成150mm",
     ["应该识别: action=modify, object=part",
      "应该提取: 修改的参数信息",
      "confidence应该>0.8"]),

    ("EXPORT-01", "导出操作",
     "把这个工程图导出为PDF格式",
     ["应该识别: action=export, object=drawing",
      "应该提取: format=pdf",
      "confidence应该>0.9"]),
]


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def test_case_case_id():
    """生成测试用例ID"""
    pass


def format_intent_result(intent):
    """格式化Intent结果用于展示"""
    lines = [
        f"✓ Action: {intent.action.value}",
        f"✓ Object: {intent.object.value}",
        f"✓ Confidence: {intent.confidence:.2f}",
        f"✓ Success: {intent.success}",
    ]

    if intent.parameters:
        lines.append(f"✓ Parameters:")
        for key, value in intent.parameters.items():
            lines.append(f"  - {key}: {value}")

    if intent.constraints:
        lines.append(f"✓ Constraints:")
        for constraint in intent.constraints:
            lines.append(f"  - {constraint}")

    if intent.error_type:
        lines.append(f"✗ Error Type: {intent.error_type}")

    if intent.error_message:
        lines.append(f"✗ Error Message: {intent.error_message}")

    return "\n".join(lines)


def compare_local_vs_claude(intent_understanding_local, intent_understanding_claude, user_input):
    """比较本地模式和Claude模式的结果"""
    print("\n" + "─" * 80)
    print("📊 模式对比")
    print("─" * 80)

    # 本地模式
    print("\n【本地模式】")
    intent_local = intent_understanding_local.understand(user_input)
    print(format_intent_result(intent_local))

    # Claude模式
    print("\n【Claude API模式】")
    try:
        intent_claude = intent_understanding_claude.understand(user_input)
        print(format_intent_result(intent_claude))

        # 对比
        print("\n【对比分析】")
        if intent_claude.success and intent_local.success:
            print(f"✓ 两种模式都成功理解输入")
            print(f"  - 本地模式置信度: {intent_local.confidence:.2f}")
            print(f"  - Claude模式置信度: {intent_claude.confidence:.2f}")
            print(f"  - 置信度提升: {(intent_claude.confidence - intent_local.confidence):.2f}")

            # 参数对比
            if intent_claude.parameters and intent_local.parameters:
                local_params = set(intent_local.parameters.keys())
                claude_params = set(intent_claude.parameters.keys())
                additional_params = claude_params - local_params
                if additional_params:
                    print(f"  - Claude额外提取的参数: {additional_params}")

        elif not intent_claude.success and intent_local.success:
            print(f"⚠ Claude模式失败，本地模式成功")
            print(f"  - Claude错误: {intent_claude.error_type or 'Unknown'}")
        elif intent_claude.success and not intent_local.success:
            print(f"✓ Claude模式成功，本地模式失败")
        else:
            print(f"✗ 两种模式都失败")

    except Exception as e:
        print(f"✗ Claude API调用失败: {e}")
        print("  提示: 请检查API密钥配置或网络连接")


def main():
    """主测试函数"""
    print_separator("=")
    print("Claude API 集成测试")
    print_separator("=")

    # 获取API密钥
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("\n⚠ 未检测到ANTHROPIC_API_KEY环境变量")
        print("\n配置方式:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\n或者直接输入API密钥 (可选，按Enter跳过):")

        user_input_key = input("> ").strip()
        if user_input_key:
            api_key = user_input_key
        else:
            print("\n⚠ 未配置API密钥，将跳过Claude API测试")
            print("仅测试本地模式...")
            api_key = None

    # 初始化意图理解引擎
    print("\n🔧 初始化意图理解引擎...")

    intent_local = IntentUnderstanding(use_claude=False)
    print("  ✓ 本地模式已初始化")

    intent_claude = None
    if api_key:
        try:
            intent_claude = IntentUnderstanding(use_claude=True, api_key=api_key)
            if intent_claude.use_claude and intent_claude.claude_client:
                print(f"  ✓ Claude API模式已初始化 (API Key: {api_key[:10]}...{api_key[-4:]})")
            else:
                print("  ⚠ Claude API模式初始化失败，anthropic包可能未安装")
                intent_claude = None
        except Exception as e:
            print(f"  ✗ Claude API模式初始化失败: {e}")
            intent_claude = None

    print()

    # 运行测试用例
    for case_id, description, user_input, expected_points in TEST_CASES:
        print_separator("=")
        print(f"测试用例: {case_id} - {description}")
        print_separator("=")
        print(f"输入: {user_input}")
        print()

        if expected_points:
            print("预期:")
            for point in expected_points:
                print(f"  • {point}")
            print()

        # 本地模式测试
        print("【本地模式结果】")
        intent_local_result = intent_local.understand(user_input)
        print(format_intent_result(intent_local_result))
        print()

        # Claude模式测试（如果可用）
        if intent_claude:
            print("【Claude API模式结果】")
            try:
                intent_claude_result = intent_claude.understand(user_input)
                print(format_intent_result(intent_claude_result))
                print()

                # 对比
                print("【对比分析】")
                if intent_claude_result.success and intent_local_result.success:
                    print(f"✓ 两种模式都成功")
                    print(f"  置信度对比:")
                    print(f"    本地: {intent_local_result.confidence:.2f}")
                    print(f"    Claude: {intent_claude_result.confidence:.2f}")
                    diff = intent_claude_result.confidence - intent_local_result.confidence
                    print(f"    提升: {diff:+.2f} {('📈' if diff > 0 else '📉')}")

                    # 参数数量对比
                    local_param_count = len(intent_local_result.parameters)
                    claude_param_count = len(intent_claude_result.parameters)
                    print(f"  参数数量:")
                    print(f"    本地: {local_param_count}")
                    print(f"    Claude: {claude_param_count}")

                    if claude_param_count > local_param_count:
                        print(f"    Claude额外提取了 {claude_param_count - local_param_count} 个参数 🎯")

                elif not intent_claude_result.success and intent_local_result.success:
                    print(f"⚠ Claude失败但本地成功")
                    print(f"  Claude错误: {intent_claude_result.error_type}")
                elif intent_claude_result.success and not intent_local_result.success:
                    print(f"✓ Claude成功但本地失败")
                else:
                    print(f"✗ 两种模式都失败")

            except Exception as e:
                print(f"✗ Claude API调用失败: {e}")

        print()

    # 总结
    print_separator("=")
    print("测试完成")
    print_separator("=")

    if intent_claude:
        print("✓ Claude API测试已完成")
        print("  可以对比两种模式的表现差异")
    else:
        print("⚠ Claude API未配置")
        print("  提示: 设置ANTHROPIC_API_KEY环境变量以测试真实API")
        print("  获取API密钥: https://console.anthropic.com/")


if __name__ == "__main__":
    main()
