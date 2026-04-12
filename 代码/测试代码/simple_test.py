# -*- coding: utf-8 -*-
"""简单测试 - 验证文档管理系统"""
import sys
import os
from pathlib import Path

print("="*60)
print("Claude Code 文档管理系统 - 系统验证")
print("="*60)
print()

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "工具脚本"))

try:
    from auto_document_manager import DocumentAutoManager

    print("[STEP 1] 初始化文档管理器")
    manager = DocumentAutoManager()
    print("状态: OK")
    print()

    print("[STEP 2] 测试文档分类")

    # 测试用例
    tests = [
        ("Agent性能研究", "research_reports"),
        ("Agent开发指南", "user_guides"),
        ("API技术文档", "technical_docs"),
    ]

    all_passed = True
    for title, expected_type in tests:
        try:
            classification = manager.classify_document(title)
            actual_type = classification["type"]

            if actual_type == expected_type:
                print(f"PASS: {title}")
                print(f"  -> {classification['directory']}")
                print(f"  -> {classification['filename']}")
            else:
                print(f"FAIL: {title}")
                print(f"  期望: {expected_type}")
                print(f"  实际: {actual_type}")
                all_passed = False
        except Exception as e:
            print(f"ERROR: {title} - {e}")
            all_passed = False

    print()
    print("[STEP 3] 测试文件保存")

    try:
        result = manager.save_document(
            "测试文档",
            "# 测试文档\n\n测试内容...",
            force_overwrite=True
        )

        if result["success"]:
            print(f"PASS: 文档保存成功")
            print(f"  路径: {result['file_path']}")

            # 验证文件
            if os.path.exists(result["file_path"]):
                print(f"PASS: 文件已创建")

                # 清理测试文件
                os.remove(result["file_path"])
                print(f"PASS: 测试文件已清理")
            else:
                print(f"FAIL: 文件未创建")
                all_passed = False
        else:
            print(f"FAIL: {result.get('message')}")
            all_passed = False

    except Exception as e:
        print(f"ERROR: 保存测试失败 - {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    print()
    print("="*60)
    if all_passed:
        print("测试结果: 所有测试通过 - 系统正常工作")
    else:
        print("测试结果: 部分测试失败 - 请检查配置")
    print("="*60)

except Exception as e:
    print(f"系统初始化失败: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("请确保:")
    print("1. auto_document_manager.py 文件存在")
    print("2. .claude/rules.json 配置文件存在")
    print("3. Python环境正常")
