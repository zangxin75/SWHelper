#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单的Python环境测试"""
import sys
import os
from pathlib import Path

print("✅ Python环境测试")
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"当前目录: {os.getcwd()}")

# 测试导入文档管理器
sys.path.insert(0, str(Path(__file__).parent.parent / "工具脚本"))

try:
    from auto_document_manager import DocumentAutoManager
    print("✅ 文档管理器导入成功")

    # 创建实例
    manager = DocumentAutoManager()
    print("✅ 文档管理器实例化成功")

    # 测试分类功能
    classification = manager.classify_document("Agent性能测试研究")
    print(f"✅ 分类测试成功: {classification['type']}")
    print(f"   目录: {classification['directory']}")
    print(f"   文件名: {classification['filename']}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 环境验证完成！")
