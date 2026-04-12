#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent功能测试脚本
测试SolidWorks AI Agent的核心功能
"""
import asyncio
import sys
import logging
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "Python脚本"))

# 配置测试日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentTestSuite:
    """Agent测试套件"""

    def __init__(self):
        self.test_results = []

    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("🧪 SolidWorks AI Agent 测试套件")
        print("="*60 + "\n")

        tests = [
            ("模块导入测试", self.test_module_imports),
            ("配置加载测试", self.test_config_loading),
            ("Agent初始化测试", self.test_agent_init),
            ("意图理解测试", self.test_intent_understanding),
            ("任务分解测试", self.test_task_decomposition),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)

            try:
                result = await test_func()
                if result["success"]:
                    print(f"✅ {test_name} 通过")
                    passed += 1
                else:
                    print(f"❌ {test_name} 失败: {result.get('error', '未知错误')}")
                    failed += 1

                self.test_results.append({
                    "name": test_name,
                    "passed": result["success"],
                    "result": result
                })

            except Exception as e:
                print(f"❌ {test_name} 异常: {e}")
                failed += 1
                self.test_results.append({
                    "name": test_name,
                    "passed": False,
                    "error": str(e)
                })

        # 输出测试汇总
        self.print_summary(passed, failed)

        return passed == len(tests)

    async def test_module_imports(self) -> dict:
        """测试模块导入"""
        try:
            # 测试基础模块
            import asyncio
            import json
            from pathlib import Path

            # 测试Agent模块（如果存在）
            try:
                from agent_coordinator import SolidWorksAgentCoordinator
                return {"success": True, "message": "所有模块导入成功"}
            except ImportError as e:
                return {
                    "success": False,
                    "error": f"Agent模块导入失败: {e}",
                    "note": "请先运行部署脚本安装依赖"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_config_loading(self) -> dict:
        """测试配置文件加载"""
        try:
            config_path = Path(__file__).parent.parent.parent / "配置" / "agent_config.json"

            if not config_path.exists():
                return {
                    "success": False,
                    "error": "配置文件不存在",
                    "note": "请运行部署脚本创建配置文件"
                }

            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证配置结构
            required_keys = ["agent_settings", "claude_settings", "solidworks_settings"]
            for key in required_keys:
                if key not in config:
                    return {
                        "success": False,
                        "error": f"配置缺少必需的键: {key}"
                    }

            return {"success": True, "message": "配置文件加载成功"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_agent_init(self) -> dict:
        """测试Agent初始化"""
        try:
            from agent_coordinator import SolidWorksAgentCoordinator

            # 创建Agent实例（使用Mock模式）
            agent = SolidWorksAgentCoordinator(use_mock=True)

            # 验证基础属性
            if not hasattr(agent, 'tools'):
                return {"success": False, "error": "Agent缺少tools属性"}

            if not hasattr(agent, 'knowledge_base'):
                return {"success": False, "error": "Agent缺少knowledge_base属性"}

            return {
                "success": True,
                "message": "Agent初始化成功",
                "tools_count": len(agent.tools)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "请确保MCP服务器路径正确"
            }

    async def test_intent_understanding(self) -> dict:
        """测试意图理解功能"""
        try:
            from agent_coordinator import SolidWorksAgentCoordinator

            agent = SolidWorksAgentCoordinator(use_mock=True)

            # 测试用例
            test_cases = [
                {
                    "input": "创建一个 100x100x50mm 的方块",
                    "expected_action": "create",
                    "expected_object": "part"
                },
                {
                    "input": "分析当前零件的质量",
                    "expected_action": "analyze",
                    "expected_object": None
                }
            ]

            results = []
            for test_case in test_cases:
                intent = await agent._understand_intent(test_case["input"])

                # 验证动作识别
                if intent["action"] != test_case["expected_action"]:
                    results.append(f"动作识别错误: 期望 {test_case['expected_action']}, 得到 {intent['action']}")
                elif test_case["expected_object"] and intent["object"] != test_case["expected_object"]:
                    results.append(f"对象识别错误: 期望 {test_case['expected_object']}, 得到 {intent['object']}")
                else:
                    results.append(f"✅ {test_case['input']}")

            return {
                "success": all("✅" in r for r in results),
                "results": results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_task_decomposition(self) -> dict:
        """测试任务分解功能"""
        try:
            from agent_coordinator import SolidWorksAgentCoordinator

            agent = SolidWorksAgentCoordinator(use_mock=True)

            # 测试意图
            intent = {
                "action": "create",
                "object": "part",
                "parameters": {
                    "dimensions": [100, 100, 50],
                    "material": "铝合金_6061"
                }
            }

            # 分解任务
            tasks = await agent._decompose_tasks(intent)

            # 验证任务序列
            if not tasks:
                return {"success": False, "error": "未能生成任务序列"}

            expected_task_types = ["create_part", "create_sketch", "create_extrude"]
            actual_task_types = [task["tool"] for task in tasks]

            for expected_type in expected_task_types:
                if expected_type not in actual_task_types:
                    return {
                        "success": False,
                        "error": f"缺少必需的任务类型: {expected_type}"
                    }

            return {
                "success": True,
                "message": "任务分解成功",
                "tasks_count": len(tasks),
                "task_types": actual_task_types
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def print_summary(self, passed: int, failed: int):
        """打印测试汇总"""
        print("\n" + "="*60)
        print("📊 测试结果汇总")
        print("="*60)

        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n总测试数: {total}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"📈 通过率: {success_rate:.1f}%")

        if failed == 0:
            print("\n🎉 所有测试通过！Agent系统可以正常使用。")
        else:
            print("\n⚠️ 部分测试失败，请检查错误信息并修复问题。")

        print("\n" + "="*60)


async def interactive_test():
    """交互式测试模式"""
    print("\n" + "="*60)
    print("🧪 交互式测试模式")
    print("="*60)
    print("\n输入测试命令，或 'quit' 退出\n")

    from agent_coordinator import SolidWorksAgentCoordinator

    try:
        agent = SolidWorksAgentCoordinator(use_mock=False)
        print("✅ Agent初始化成功（实际模式）")
    except Exception as e:
        print(f"⚠️ Agent初始化失败: {e}")
        print("切换到Mock模式...")
        agent = SolidWorksAgentCoordinator(use_mock=True)
        print("✅ Agent初始化成功（Mock模式）")

    while True:
        try:
            user_input = input("👤 测试输入: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                break

            if not user_input:
                continue

            print(f"\n🤖 处理: {user_input}")

            result = await agent.process_design_request(user_input)

            if result["success"]:
                print(f"✅ {result['feedback']}")
            else:
                print(f"❌ 处理失败: {result.get('message', '未知错误')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n👋 测试结束")


if __name__ == "__main__":
    import sys

    # 选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # 交互式测试
        asyncio.run(interactive_test())
    else:
        # 自动化测试
        test_suite = AgentTestSuite()
        success = asyncio.run(test_suite.run_all_tests())

        sys.exit(0 if success else 1)
