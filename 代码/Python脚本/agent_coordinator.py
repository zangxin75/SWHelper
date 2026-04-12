"""
Agent Coordinator Module

主协调器，集成所有6个模块，实现端到端的设计自动化流程

模块集成:
1. Knowledge Base - 设计知识库
2. Intent Engine - 意图理解
3. Task Decomposer - 任务分解
4. Tool Registry - 工具注册
5. Task Executor - 任务执行
6. Result Validator - 结果验证

需求文件: 文档/需求/req_coordinator.md
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from knowledge_base import KnowledgeBase
from intent_understanding import IntentUnderstanding, IntentAction, IntentObject
from task_decomposer import TaskDecomposer
from task_executor import TaskExecutor
from result_validator import ResultValidator
from schemas import Intent, Task, ExecutionResult, ValidationReport


@dataclass
class CoordinatorResult:
    """协调器结果"""
    success: bool                    # 整体是否成功
    feedback: str                    # 用户友好的反馈信息
    total_time: float                # 总执行时间

    # 模式配置
    mode: str                        # "mock" or "real_solidworks"

    # 执行统计
    tasks_executed: int = 0          # 执行的任务数
    tasks_passed: int = 0            # 通过的任务数

    # 各阶段结果
    intent: Optional[str] = None     # 意图（字符串形式）
    tasks: Optional[List[Dict]] = None  # 任务列表
    execution_results: Optional[List[Dict]] = None  # 执行结果
    validation_results: Optional[Dict] = None  # 验证结果

    # 错误信息
    error_type: Optional[str] = None # 错误类型
    error_message: Optional[str] = None  # 错误详情

    # 时间分解
    time_breakdown: Optional[Dict[str, float]] = None  # 各阶段耗时


class AgentCoordinator:
    """
    AI设计代理协调器

    功能:
    - 集成所有6个模块
    - 端到端处理设计请求
    - 生成用户友好的反馈
    - 处理错误和异常
    - 跟踪执行时间
    """

    def __init__(self, use_claude: bool = False, use_real_sw: bool = False,
                 api_key: Optional[str] = None):
        """
        初始化协调器

        Args:
            use_claude: 是否使用Claude API进行意图理解
            use_real_sw: 是否使用真实SolidWorks（False则使用mock模式）
            api_key: Claude API密钥
        """
        self.use_claude = use_claude
        self.use_real_sw = use_real_sw

        # 初始化所有6个模块
        self._init_modules(api_key)

    def _init_modules(self, api_key: Optional[str]):
        """初始化所有模块"""
        # 1. 知识库
        self.knowledge_base = KnowledgeBase()

        # 2. 意图引擎
        self.intent_engine = IntentUnderstanding(
            use_claude=self.use_claude,
            api_key=api_key
        )

        # 3. 任务分解器
        self.decomposer = TaskDecomposer()

        # 4. 工具注册表（集成到执行器中）
        self.tool_registry = {}  # 将在执行器中注册

        # 5. 任务执行器
        self.executor = TaskExecutor()
        self._register_tools()

        # 6. 结果验证器
        kb_dict = {
            "min_thickness": 3,
            "min_draft": 1,
            "min_fillet": 1
        }
        self.validator = ResultValidator(knowledge_base=kb_dict)

    def _register_tools(self):
        """注册工具函数到执行器"""
        # Mock工具函数
        async def mock_create_part(**kwargs):
            return {
                "success": True,
                "result": "mock_part_created",
                "tool_name": "create_part",
                "execution_time": 0.1
            }

        async def mock_modify_part(**kwargs):
            return {
                "success": True,
                "result": "mock_part_modified",
                "tool_name": "modify_part",
                "execution_time": 0.1
            }

        async def mock_add_fillet(**kwargs):
            return {
                "success": True,
                "result": "mock_fillet_added",
                "tool_name": "add_fillet",
                "execution_time": 0.05
            }

        async def mock_add_chamfer(**kwargs):
            return {
                "success": True,
                "result": "mock_chamfer_added",
                "tool_name": "add_chamfer",
                "execution_time": 0.05
            }

        # 注册mock工具
        self.executor.register_tool("create_part", mock_create_part)
        self.executor.register_tool("modify_part", mock_modify_part)
        self.executor.register_tool("add_fillet", mock_add_fillet)
        self.executor.register_tool("add_chamfer", mock_add_chamfer)

        # TODO: 注册真实SolidWorks工具（当use_real_sw=True时）

    def process_design_request(self, user_input: str) -> CoordinatorResult:
        """
        处理设计请求（主入口）

        流程:
        1. 意图理解 (Intent Understanding)
        2. 任务分解 (Task Decomposition)
        3. 任务执行 (Task Execution)
        4. 结果验证 (Result Validation)
        5. 生成反馈 (Generate Feedback)

        Args:
            user_input: 用户自然语言输入

        Returns:
            CoordinatorResult: 完整的执行结果
        """
        total_start = time.perf_counter()

        # 初始化时间分解
        time_breakdown = {}

        # 初始化结果
        result = CoordinatorResult(
            success=False,
            feedback="",
            total_time=0.0,
            mode="real_solidworks" if self.use_real_sw else "mock",
            time_breakdown=time_breakdown
        )

        try:
            # ========== 阶段1: 意图理解 ==========
            intent_start = time.perf_counter()
            intent_result = self._understand_intent(user_input, result)
            intent_time = time.perf_counter() - intent_start
            time_breakdown["intent_time"] = intent_time

            if not intent_result:
                # 意图理解失败
                result.feedback = self._generate_error_feedback(
                    "IntentError",
                    "无法理解您的设计意图，请提供更清晰的描述",
                    user_input
                )
                result.total_time = time.perf_counter() - total_start
                return result

            # ========== 阶段2: 任务分解 ==========
            decomp_start = time.perf_counter()
            tasks = self._decompose_tasks(intent_result, result)
            decomp_time = time.perf_counter() - decomp_start
            time_breakdown["decomposition_time"] = decomp_time

            if not tasks:
                # 任务分解失败或无任务
                result.feedback = self._generate_error_feedback(
                    "NoTasksError",
                    "无法从您的设计意图中生成可执行任务，请提供更具体的设计参数",
                    user_input
                )
                result.total_time = time.perf_counter() - total_start
                return result

            # ========== 阶段3: 任务执行 ==========
            exec_start = time.perf_counter()
            execution_result = self._execute_tasks(tasks, result)
            exec_time = time.perf_counter() - exec_start
            time_breakdown["execution_time"] = exec_time

            if not execution_result or execution_result.failure_count > 0:
                # 任务执行失败
                result.feedback = self._generate_execution_feedback(
                    execution_result,
                    tasks,
                    partial_success=execution_result.success_count > 0 if execution_result else False
                )
                result.total_time = time.perf_counter() - total_start
                return result

            # ========== 阶段4: 结果验证 ==========
            val_start = time.perf_counter()
            validation_result = self._validate_results(execution_result, intent_result, result)
            val_time = time.perf_counter() - val_start
            time_breakdown["validation_time"] = val_time

            # ========== 阶段5: 生成反馈 ==========
            result.feedback = self._generate_success_feedback(
                intent_result,
                tasks,
                execution_result,
                validation_result
            )

            result.success = True

        except Exception as e:
            # 捕获未预期的异常
            result.success = False
            result.error_type = type(e).__name__
            result.error_message = str(e)
            result.feedback = self._generate_error_feedback(
                type(e).__name__,
                f"处理过程中发生错误: {str(e)}",
                user_input
            )

        finally:
            # 记录总时间
            result.total_time = time.perf_counter() - total_start

        return result

    def _understand_intent(self, user_input: str, result: CoordinatorResult) -> Optional[Dict]:
        """理解用户意图"""
        if not user_input or not user_input.strip():
            result.error_type = "IntentError"
            return None

        try:
            intent_dict = self.intent_engine.understand(user_input)

            # 检查是否理解失败
            if intent_dict.get("confidence", 0) == 0:
                result.error_type = "IntentError"
                result.error_message = intent_dict.get("error", "无法理解输入")
                return None

            # 保存意图到结果
            result.intent = f"{intent_dict.get('action', 'unknown')}_{intent_dict.get('object', 'unknown')}"

            return intent_dict

        except Exception as e:
            result.error_type = "IntentError"
            result.error_message = str(e)
            return None

    def _decompose_tasks(self, intent_dict: Dict, result: CoordinatorResult) -> List[Task]:
        """分解意图为任务"""
        try:
            # 获取action和object，处理枚举类型
            action_value = intent_dict.get("action")
            if hasattr(action_value, 'value'):
                action_value = action_value.value

            object_value = intent_dict.get("object")
            if hasattr(object_value, 'value'):
                object_value = object_value.value
            # 如果object不是有效值，默认为part
            if object_value not in ["part", "assembly", "drawing"]:
                object_value = "part"

            # 构建Intent对象
            intent = Intent(
                action=action_value or "create",
                object=object_value,
                parameters={
                    "dimensions": intent_dict.get("dimensions"),
                    "material": intent_dict.get("material"),
                },
                confidence=intent_dict.get("confidence", 0.0),
                raw_input=""
            )

            # 尝试复杂分解
            tasks = self.decomposer.decompose_complex(intent)

            # 如果复杂分解没有产生额外任务，使用简单分解
            if len(tasks) == 1:
                tasks = self.decomposer.decompose(intent)

            if not tasks:
                result.error_type = "DecompositionError"
                return []

            # 保存任务到结果
            result.tasks = [
                {
                    "id": task.id,
                    "tool": task.tool,
                    "description": task.description,
                    "parameters": task.parameters
                }
                for task in tasks
            ]

            return tasks

        except Exception as e:
            result.error_type = "DecompositionError"
            result.error_message = str(e)
            return []

    def _execute_tasks(self, tasks: List[Task], result: CoordinatorResult) -> Optional[ExecutionResult]:
        """执行任务序列"""
        try:
            import asyncio

            # 运行异步执行
            execution_result = asyncio.run(self.executor.execute(tasks))

            # 更新统计
            result.tasks_executed = execution_result.success_count + execution_result.failure_count
            result.tasks_passed = execution_result.success_count

            # 保存执行结果
            result.execution_results = [
                {
                    "success": r.success,
                    "tool_name": r.tool_name,
                    "result": str(r.result) if r.result else None,
                    "error": r.error,
                    "execution_time": r.execution_time
                }
                for r in execution_result.results
            ]

            return execution_result

        except Exception as e:
            result.error_type = "ExecutionError"
            result.error_message = str(e)
            return None

    def _validate_results(self, execution_result: ExecutionResult, intent_dict: Dict,
                         result: CoordinatorResult) -> ValidationReport:
        """验证执行结果"""
        try:
            # 转换执行结果为验证器需要的格式
            results_list = [
                {
                    "success": r.success,
                    "tool_name": r.tool_name,
                    "result": r.result
                }
                for r in execution_result.results
            ]

            # 执行验证
            validation_report = self.validator.validate(results_list, intent_dict)

            # 保存验证结果
            result.validation_results = {
                "success": validation_report.success,
                "passed": validation_report.passed,
                "failed": validation_report.failed,
                "warnings": validation_report.warnings,
                "errors": validation_report.errors,
                "suggestions": validation_report.suggestions,
                "metrics": validation_report.metrics
            }

            return validation_report

        except Exception as e:
            result.error_type = "ValidationError"
            result.error_message = str(e)
            # 返回一个失败的验证报告
            return ValidationReport(success=False)

    def _generate_success_feedback(self, intent_dict: Dict, tasks: List[Task],
                                   execution_result: ExecutionResult,
                                   validation_report: ValidationReport) -> str:
        """生成成功反馈"""
        feedback_parts = []

        # 1. 意图确认
        action = intent_dict.get("action", "创建")
        obj = intent_dict.get("object", "零件")
        feedback_parts.append(f"✓ 已理解您的设计意图: {action} {obj}")

        # 2. 执行摘要
        feedback_parts.append(f"✓ 成功执行 {execution_result.success_count} 个任务")

        # 3. 验证结果
        if validation_report.success:
            feedback_parts.append("✓ 设计验证通过")
        else:
            feedback_parts.append(f"⚠ 设计验证发现 {len(validation_report.warnings)} 个警告")

        # 4. 建议
        if validation_report.suggestions:
            feedback_parts.append("\n改进建议:")
            for suggestion in validation_report.suggestions[:3]:  # 最多显示3条
                feedback_parts.append(f"  - {suggestion}")

        # 5. 时间信息
        if execution_result.total_time > 0:
            feedback_parts.append(f"\n⏱ 总耗时: {execution_result.total_time:.2f}秒")

        return "\n".join(feedback_parts)

    def _generate_execution_feedback(self, execution_result: Optional[ExecutionResult],
                                    tasks: List[Task], partial_success: bool) -> str:
        """生成执行反馈（处理失败场景）"""
        if not execution_result:
            return "❌ 任务执行失败: 无法获取执行结果"

        if partial_success:
            return (f"⚠ 部分成功: {execution_result.success_count}/{len(tasks)} 个任务执行成功\n"
                   f"失败任务: {', '.join(execution_result.failed_tasks[:5])}")

        return f"❌ 任务执行失败: {execution_result.failure_count} 个任务失败"

    def _generate_error_feedback(self, error_type: str, error_message: str,
                                user_input: str) -> str:
        """生成错误反馈"""
        feedback = f"❌ 错误 ({error_type}): {error_message}"

        # 根据错误类型提供建议
        suggestions = {
            "IntentError": "建议: 请使用更清晰的设计描述，例如'创建一个100x100x50的立方体'",
            "NoTasksError": "建议: 请提供具体的设计参数，例如尺寸、材料等",
            "DecompositionError": "建议: 请确认您的描述包含明确的设计操作和对象",
            "ExecutionError": "建议: 请检查设计参数是否合理，或稍后重试",
            "ValidationError": "建议: 请检查设计是否符合规范要求"
        }

        if error_type in suggestions:
            feedback += f"\n{suggestions[error_type]}"

        return feedback
