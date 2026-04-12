"""
SolidWorks Agent - Interactive Demo Script

交互式演示脚本，展示Agent的核心功能
Interactive demonstration script showing core agent capabilities

功能演示:
1. 创建100x100x50mm铝制长方体 (Create 100x100x50mm aluminum block)
2. 分析质量属性 (Analyze mass properties)
3. 导出STEP格式 (Export STEP format)

Usage:
    python demo.py                    # Interactive mode
    python demo.py --auto             # Automatic demo mode
    python demo.py --real-sw          # Use real SolidWorks (requires SW installed)
"""

import sys
import argparse
from pathlib import Path
import io

# 设置UTF-8编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "代码/Python脚本"))

from agent_coordinator import AgentCoordinator


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def print_section(title):
    """打印章节标题"""
    print()
    print_separator()
    print(f"  {title}")
    print_separator()
    print()


def demo_create_block(coordinator, dimensions="100x100x50", material="铝"):
    """演示：创建长方体"""
    print_section("演示1: 创建参数化长方体")

    user_input = f"创建一个{dimensions}毫米的{material}制长方体"

    print(f"用户输入: {user_input}")
    print(f"工作模式: {'模拟' if not coordinator.use_real_sw else '真实SolidWorks'}")
    print()
    print("处理中...")

    result = coordinator.process_design_request(user_input)

    print()
    print("[OK] 处理完成")
    print(f"  状态: {'成功' if result.success else '失败'}")
    print(f"  耗时: {result.total_time:.2f}秒")
    print(f"  执行任务数: {result.tasks_executed}")
    print(f"  通过任务数: {result.tasks_passed}")
    print()
    print("反馈信息:")
    print(f"  {result.feedback}")

    if result.intent:
        print()
        print("识别的意图:")
        print(f"  {result.intent}")

    if result.tasks:
        print()
        print("分解的任务:")
        for i, task in enumerate(result.tasks, 1):
            print(f"  {i}. {task.get('tool_name', 'unknown')}: {task.get('description', '')}")

    return result


def demo_analyze_mass(coordinator, dimensions="50x50x50"):
    """演示：分析质量属性"""
    print_section("演示2: 质量属性分析")

    user_input = f"创建一个{dimensions}毫米的钢制立方体并分析质量"

    print(f"用户输入: {user_input}")
    print()
    print("处理中...")

    result = coordinator.process_design_request(user_input)

    print()
    print("[OK] 分析完成")
    print(f"  状态: {'成功' if result.success else '失败'}")
    print(f"  耗时: {result.total_time:.2f}秒")
    print()
    print("分析结果:")
    print(f"  {result.feedback}")

    return result


def demo_export_step(coordinator, model_name="零件"):
    """演示：导出STEP格式"""
    print_section("演示3: 导出STEP格式")

    user_input = f"创建一个80x80x40的长方体并导出为STEP格式"

    print(f"用户输入: {user_input}")
    print()
    print("处理中...")

    result = coordinator.process_design_request(user_input)

    print()
    print("[OK] 导出完成")
    print(f"  状态: {'成功' if result.success else '失败'}")
    print(f"  耗时: {result.total_time:.2f}秒")
    print()
    print("导出信息:")
    print(f"  {result.feedback}")

    return result


def demo_complex_workflow(coordinator):
    """演示：复杂工作流"""
    print_section("演示4: 复杂设计工作流")

    workflows = [
        "创建一个100x100x50毫米的长方体",
        "在顶部边缘添加10mm倒角",
        "分析模型质量属性",
    ]

    results = []

    for i, user_input in enumerate(workflows, 1):
        print()
        print(f"步骤 {i}/{len(workflows)}: {user_input}")
        print("处理中...")

        result = coordinator.process_design_request(user_input)
        results.append(result)

        print(f"[OK] 完成 - {'成功' if result.success else '失败'}")
        print(f"  {result.feedback}")

    return results


def interactive_demo(coordinator):
    """交互式演示模式"""
    print_section("SolidWorks Agent - 交互式演示")

    print("可用命令:")
    print("  1 - 创建长方体")
    print("  2 - 质量分析")
    print("  3 - 导出STEP")
    print("  4 - 复杂工作流")
    print("  5 - 自定义输入")
    print("  q - 退出")
    print()

    while True:
        try:
            cmd = input("请输入命令 (1-5/q): ").strip().lower()

            if cmd == 'q':
                print("退出演示")
                break

            elif cmd == '1':
                dimensions = input("  输入尺寸 (默认 100x100x50): ").strip() or "100x100x50"
                material = input("  输入材料 (默认 铝): ").strip() or "铝"
                demo_create_block(coordinator, dimensions, material)

            elif cmd == '2':
                dimensions = input("  输入尺寸 (默认 50x50x50): ").strip() or "50x50x50"
                demo_analyze_mass(coordinator, dimensions)

            elif cmd == '3':
                demo_export_step(coordinator)

            elif cmd == '4':
                demo_complex_workflow(coordinator)

            elif cmd == '5':
                user_input = input("  请输入您的需求: ").strip()
                if user_input:
                    print()
                    print("处理中...")
                    result = coordinator.process_design_request(user_input)
                    print()
                    print("[OK] 处理完成")
                    print(f"  状态: {'成功' if result.success else '失败'}")
                    print(f"  耗时: {result.total_time:.2f}秒")
                    print()
                    print("反馈:")
                    print(f"  {result.feedback}")

            else:
                print("无效命令，请重新输入")

            print()

        except KeyboardInterrupt:
            print("\n\n退出演示")
            break
        except Exception as e:
            print(f"错误: {e}")
            print()


def auto_demo(coordinator):
    """自动演示模式"""
    print_section("SolidWorks Agent - 自动演示")

    print("Claude AI:", "启用" if coordinator.use_claude else "禁用")
    print("真实SolidWorks:", "启用" if coordinator.use_real_sw else "模拟模式")
    print()

    # 演示1: 创建长方体
    demo_create_block(coordinator)

    input("\n按Enter继续...")

    # 演示2: 质量分析
    demo_analyze_mass(coordinator)

    input("\n按Enter继续...")

    # 演示3: 导出STEP
    demo_export_step(coordinator)

    input("\n按Enter继续...")

    # 演示4: 复杂工作流
    demo_complex_workflow(coordinator)

    print()
    print_section("演示完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SolidWorks Agent - 交互式演示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python demo.py              # 交互式模式
    python demo.py --auto       # 自动演示模式
    python demo.py --real-sw    # 使用真实SolidWorks
        """
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="自动演示模式"
    )

    parser.add_argument(
        "--real-sw",
        action="store_true",
        help="使用真实SolidWorks（需要安装SW）"
    )

    parser.add_argument(
        "--claude",
        action="store_true",
        help="启用Claude AI（需要API密钥）"
    )

    args = parser.parse_args()

    # 创建Coordinator
    print("初始化Agent...")
    coordinator = AgentCoordinator(
        use_claude=args.claude,
        use_real_sw=args.real_sw
    )
    print("[OK] Agent初始化完成")
    print()

    # 运行演示
    if args.auto:
        auto_demo(coordinator)
    else:
        interactive_demo(coordinator)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
