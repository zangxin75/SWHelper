"""
Simple Claude API Test Script

Usage:
    1. Set API key: export ANTHROPIC_API_KEY="your-key"
    2. Run: python test_claude_simple.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent / "代码" / "Python脚本"
sys.path.insert(0, str(project_root))

from intent_understanding import IntentUnderstanding


def print_header(text):
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)


def print_intent(intent, mode="Local"):
    print(f"\n[{mode} Mode Result]")
    print(f"  Action: {intent.action.value}")
    print(f"  Object: {intent.object.value}")
    print(f"  Confidence: {intent.confidence:.2f}")
    print(f"  Success: {intent.success}")

    if intent.parameters:
        print(f"  Parameters:")
        for key, value in intent.parameters.items():
            print(f"    - {key}: {value}")

    if intent.error_type:
        print(f"  Error: {intent.error_type}")
        if intent.error_message:
            print(f"    Message: {intent.error_message}")


def main():
    print_header("Claude API Integration Test")

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("\n[!] ANTHROPIC_API_KEY not found in environment")
        print("\nTo configure:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nGet API key at: https://console.anthropic.com/")
        print("\n[*] Testing local mode only...\n")

    # Initialize engines
    print("[*] Initializing intent understanding engines...")

    intent_local = IntentUnderstanding(use_claude=False)
    print("  [+] Local mode initialized")

    intent_claude = None
    if api_key:
        try:
            intent_claude = IntentUnderstanding(use_claude=True, api_key=api_key)
            if intent_claude.use_claude and intent_claude.claude_client:
                key_preview = f"{api_key[:10]}...{api_key[-4:]}"
                print(f"  [+] Claude API mode initialized (Key: {key_preview})")
            else:
                print("  [-] Claude API mode initialization failed")
                print("      Hint: anthropic package may not be installed")
                intent_claude = None
        except Exception as e:
            print(f"  [-] Claude API mode initialization failed: {e}")
            intent_claude = None

    # Test cases
    test_cases = [
        ("Complex Part Design",
         "设计一个轴承座，底座200x150x20mm，支撑高度100mm，顶部有直径50mm的孔，使用45号钢"),

        ("Drawing Creation",
         "创建一个工程图，使用A3图纸，1:2比例，包含3个视图"),

        ("Assembly Design",
         "创建一个装配体，包含5个零件，使用同轴配合，检查干涉"),

        ("Modification",
         "修改这个零件，把高度从100mm改成150mm"),

        ("Export",
         "把这个工程图导出为PDF格式"),
    ]

    for title, user_input in test_cases:
        print_header(f"Test: {title}")
        print(f"\nInput: {user_input}")

        # Test local mode
        intent_local_result = intent_local.understand(user_input)
        print_intent(intent_local_result, "Local")

        # Test Claude mode (if available)
        if intent_claude:
            try:
                intent_claude_result = intent_claude.understand(user_input)
                print_intent(intent_claude_result, "Claude API")

                # Compare
                print(f"\n[Comparison]")
                if intent_claude_result.success and intent_local_result.success:
                    conf_diff = intent_claude_result.confidence - intent_local_result.confidence
                    print(f"  Confidence: Local={intent_local_result.confidence:.2f}, "
                          f"Claude={intent_claude_result.confidence:.2f} "
                          f"({conf_diff:+.2f})")

                    local_params = len(intent_local_result.parameters)
                    claude_params = len(intent_claude_result.parameters)
                    print(f"  Parameters: Local={local_params}, Claude={claude_params}")

                    if claude_params > local_params:
                        print(f"  [+] Claude extracted {claude_params - local_params} extra parameters!")

                elif not intent_claude_result.success and intent_local_result.success:
                    print(f"  [!] Claude failed but local succeeded")
                elif intent_claude_result.success and not intent_local_result.success:
                    print(f"  [+] Claude succeeded but local failed!")
                else:
                    print(f"  [-] Both modes failed")

            except Exception as e:
                print(f"\n[!] Claude API call failed: {e}")

    # Summary
    print_header("Summary")
    if intent_claude:
        print("[+] Claude API test completed")
        print("    You can compare the performance of both modes")
        print("\n[*] Key observations:")
        print("    - Claude typically has higher confidence")
        print("    - Claude can extract more parameters")
        print("    - Local mode is faster and works offline")
    else:
        print("[!] Claude API not configured")
        print("\n[*] To test Claude API:")
        print("    1. Get API key: https://console.anthropic.com/")
        print("    2. Set environment variable:")
        print("       export ANTHROPIC_API_KEY='your-key'")
        print("    3. Run this script again")
        print("\n[*] Current test results show local mode capabilities")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
