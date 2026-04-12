# 🧪 文档管理系统测试脚本

import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "工具脚本"))

from auto_document_manager import DocumentAutoManager

def test_classification():
    """测试文档分类功能"""
    print("="*60)
    print("🧪 测试1: 文档分类")
    print("="*60)

    manager = DocumentAutoManager()

    test_cases = [
        ("Agent性能测试研究报告", "research_reports"),
        ("Agent开发快速启动指南", "user_guides"),
        ("MCP服务器API文档", "technical_docs"),
        ("项目计划总结", "project_management"),
    ]

    passed = 0
    failed = 0

    for title, expected_type in test_cases:
        classification = manager.classify_document(title)

        if classification["type"] == expected_type:
            print(f"✅ {title}")
            print(f"   类型: {classification['type']}")
            print(f"   路径: {classification['directory']}")
            passed += 1
        else:
            print(f"❌ {title}")
            print(f"   期望: {expected_type}")
            print(f"   实际: {classification['type']}")
            failed += 1
        print()

    print(f"测试结果: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)

def test_filename_generation():
    """测试文件名生成"""
    print("="*60)
    print("🧪 测试2: 文件名生成")
    print("="*60)

    manager = DocumentAutoManager()

    test_cases = [
        ("技术研究", "研究报告", "_研究报告.md"),
        ("快速指南", "快速启动指南", "_快速启动指南.md"),
    ]

    passed = 0
    failed = 0

    for title, expected_keyword, expected_suffix in test_cases:
        classification = manager.classify_document(title)
        filename = classification["filename"]

        if expected_keyword in filename and filename.endswith(expected_suffix):
            print(f"✅ {title}")
            print(f"   文件名: {filename}")
            passed += 1
        else:
            print(f"❌ {title}")
            print(f"   文件名: {filename}")
            print(f"   期望包含: {expected_keyword}{expected_suffix}")
            failed += 1
        print()

    print(f"测试结果: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)

def test_path_creation():
    """测试目录创建"""
    print("="*60)
    print("🧪 测试3: 目录创建")
    print("="*60)

    manager = DocumentAutoManager()

    # 测试保存文档（会自动创建目录）
    result = manager.save_document(
        "测试文档",
        "# 测试文档\n\n这是测试内容...",
        force_overwrite=True
    )

    if result["success"]:
        print(f"✅ 文档保存成功")
        print(f"   路径: {result['file_path']}")

        # 验证文件存在
        if os.path.exists(result["file_path"]):
            print(f"✅ 文件已创建")
            return True
        else:
            print(f"❌ 文件未创建")
            return False
    else:
        print(f"❌ 保存失败: {result.get('error')}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Claude Code 文档管理系统测试套件")
    print("="*60 + "\n")

    tests = [
        ("文档分类测试", test_classification),
        ("文件名生成测试", test_filename_generation),
        ("目录创建测试", test_path_creation),
    ]

    results = []
    for test_name, test_func in tests:
        print()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            results.append((test_name, False))

    # 汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！文档管理系统工作正常。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
