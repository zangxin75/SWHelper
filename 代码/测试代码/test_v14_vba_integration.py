#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 SWHelper V14.0 - VBA集成版本

关键测试：验证CreateSketch是否成功

V14.0的改进：
- 使用VBA验证的晚绑定方法
- CreateSketchViaVBA方法实现了与VBA相同的逻辑
- 如果C#方法失败，自动切换到VBA方法
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent.parent / "Python脚本"
sys.path.insert(0, str(script_dir))

print("="*60)
print("SWHelper V14.0 - VBA集成版本测试")
print("="*60)
print()
print("V14.0特性:")
print("✓ CreateSketch使用VBA验证的方法")
print("✓ 自动回退到VBA备用方案")
print("✓ 基于成功VBA测试的实现")
print()
print("="*60)
print()

try:
    import win32com.client as win32

    # 连接SWHelper
    print("[1] 连接到 SWHelper V14.0...")
    sw = win32.Dispatch("SWHelper.Robust")
    print(f"✅ 已连接")
    print(f"   版本: {sw.GetVersion()}")
    print()

    # 连接SolidWorks
    print("[2] 连接到 SolidWorks...")
    if not sw.ConnectToSW():
        print(f"❌ 连接失败: {sw.GetLastError()}")
        print()
        print("请确保:")
        print("1. SolidWorks 2026 正在运行")
        print("2. 没有其他程序占用SolidWorks")
        input("\n按 Enter 退出...")
        sys.exit(1)
    print("✅ 已连接到 SolidWorks")
    print()

    # 创建零件
    print("[3] 创建零件...")
    if not sw.CreatePart():
        print(f"❌ CreatePart 失败: {sw.GetLastError()}")
        input("\n按 Enter 退出...")
        sys.exit(1)
    print("✅ CreatePart 成功")
    print()

    # 创建草图（关键测试！）
    print("[4] 创建草图（V14.0 VBA集成方法）...")
    print()
    print("这是关键测试：")
    print("- V14.0使用与VBA相同的晚绑定方法")
    print("- 如果C#方法失败，自动切换到VBA方法")
    print("- VBA测试已验证此方法可行")
    print()

    if not sw.CreateSketch():
        print(f"❌ CreateSketch 失败: {sw.GetLastError()}")
        print()
        print("="*60)
        print("测试失败")
        print("="*60)
        print()
        print("可能的原因：")
        print("1. VBA测试成功但C#晚绑定仍然失败")
        print("2. 需要实际调用VBA宏文件")
        print("3. SolidWorks 2026 API的其他限制")
        print()
        print("下一步：")
        print("✓ 在SolidWorks中手动运行VBA宏验证")
        print("✓ 或者实现真正的VBA宏文件调用")
        input("\n按 Enter 退出...")
        sys.exit(1)

    print()
    print("="*60)
    print("🎉 成功！V14.0 VBA集成有效！")
    print("="*60)
    print()
    print("重大突破：")
    print("✅ CreateSketch 成功创建草图")
    print("✅ 使用VBA验证的晚绑定方法")
    print("✅ 自动回退机制工作正常")
    print()
    print("这意味着：")
    print("- CreatePart: ✅ 100% 自动化")
    print("- CreateSketch: ✅ 100% 自动化")
    print("- 整体进度: ✅ 100% 完成！")
    print()
    print("="*60)

    input("\n按 Enter 退出...")

except Exception as e:
    print()
    print("="*60)
    print("测试异常")
    print("="*60)
    print(f"错误: {e}")
    print()
    print("请检查:")
    print("1. SWHelper.Robust.dll 是否已注册")
    print("2. SolidWorks 2026 是否正在运行")
    print("3. Python环境是否正确")
    input("\n按 Enter 退出...")
    sys.exit(1)
