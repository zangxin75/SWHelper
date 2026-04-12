#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文档管理系统测试脚本 - 不使用特殊字符"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("Claude Code 文档管理系统测试")
print("=" * 60)
print()

# 测试1: Python环境
print("[TEST 1] Python环境检查")
print(f"Python版本: {sys.version}")
print(f"Python可执行文件: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")
print("Python环境: OK")
print()

# 测试2: 模块导入
print("[TEST 2] 模块导入测试")
sys.path.insert(0, str(Path(__file__).parent.parent / "工具脚本"))

try:
    from auto_document_manager import DocumentAutoManager
    print("auto_document_manager模块导入: OK")
except Exception as e:
    print(f"模块导入失败: {e}")
    sys.exit(1)

print()

# 测试3: 文档分类
print("[TEST 3] 文档分类功能测试")
try:
    manager = DocumentAutoManager()

    test_cases = [
        ("Agent性能测试研究", "research_reports"),
        ("Agent开发快速指南", "user_guides"),
        ("MCP服务器API文档", "technical_docs"),
    ]

    passed = 0
    total = len(test_cases)

    for title, expected_type in test_cases:
        classification = manager.classify_document(title)

        if classification["type"] == expected_type:
            print(f"✓ {title}")
            print(f"  类型: {classification['type']}")
            print(f"  目录: {classification['directory']}")
            print(f"  文件名: {classification['filename']}")
            passed += 1
        else:
            print(f"✗ {title}")
            print(f"  期望类型: {expected_type}")
            print(f"  实际类型: {classification['type']}")
        print()

    print(f"分类测试结果: {passed}/{total} 通过")

except Exception as e:
    print(f"分类测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试4: 文件名生成
print("[TEST 4] 文件名生成测试")
try:
    test_titles = [
        "技术研究",
        "快速指南",
        "API文档"
    ]

    for title in test_titles:
        classification = manager.classify_document(title)
        filename = classification["filename"]

        # 检查是否包含中文
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in filename)

        # 检查是否使用下划线
        has_underscore = '_' in filename

        if has_chinese and has_underscore:
            print(f"✓ {title} -> {filename}")
        else:
            print(f"✗ {title} -> {filename}")
            if not has_chinese:
                print("  问题: 不包含中文")
            if not has_underscore:
                print("  问题: 不使用下划线")

    print("文件名生成测试完成")

except Exception as e:
    print(f"文件名生成测试失败: {e}")

print()

# 测试5: 目录创建
print("[TEST 5] 目录创建和文件保存测试")
try:
    manager = DocumentAutoManager()

    # 创建测试文档
    test_title = "系统测试文档"
    test_content = "# 系统测试文档\n\n这是测试内容，验证文档管理系统是否正常工作。"

    result = manager.save_document(test_title, test_content, force_overwrite=True)

    if result["success"]:
        print(f"✓ 文档保存成功")
        print(f"  路径: {result['file_path']}")

        # 验证文件存在
        if os.path.exists(result["file_path"]):
            print(f"✓ 文件已创建")

            # 读取文件内容验证
            with open(result["file_path"], 'r', encoding='utf-8') as f:
                content = f.read()
                if test_content.split('\n')[0] in content:
                    print(f"✓ 内容验证成功")
                else:
                    print(f"✗ 内容不匹配")

            # 清理测试文件
            try:
                os.remove(result["file_path"])
                print(f"✓ 测试文件已清理")
            except:
                print(f"⚠ 测试文件未清理")
        else:
            print(f"✗ 文件未创建")
    else:
        print(f"✗ 保存失败: {result.get('message')}")

except Exception as e:
    print(f"目录创建测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("测试完成")
print("=" * 60)

# 汇总
print("\n测试总结:")
print("1. Python环境: 检查完成")
print("2. 模块导入: 检查完成")
print("3. 文档分类: 检查完成")
print("4. 文件名生成: 检查完成")
print("5. 目录创建: 检查完成")
print("\n请查看上面的测试结果以确认系统状态。")
