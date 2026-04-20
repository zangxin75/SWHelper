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
from intent_understanding import IntentUnderstanding
from task_decomposition import TaskDecomposer
from task_executor import TaskExecutor
from result_validator import ResultValidator
from schemas import Intent, Task, ExecutionResult, ValidationReport, ActionType, ObjectType


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
                 use_real_mcp: bool = False, api_key: Optional[str] = None):
        """
        初始化协调器

        Args:
            use_claude: 是否使用Claude API进行意图理解
            use_real_sw: 是否使用真实SolidWorks（False则使用mock模式）
            use_real_mcp: 是否使用真实MCP Server（ENH-07）
            api_key: Claude API密钥
        """
        self.use_claude = use_claude
        self.use_real_sw = use_real_sw
        self.use_real_mcp = use_real_mcp or use_real_sw  # use_real_sw implies MCP

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
        # ENH-07: 传递MCP配置
        mcp_config = {
            "command": "python",
            "args": ["-m", "solidworks_mcp"],
            "timeout": 30.0
        }
        self.executor = TaskExecutor(
            use_real_mcp=self.use_real_mcp,
            mcp_config=mcp_config
        )
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

        # FIX-03: 添加复合操作需要的mock工具
        async def mock_calculate_mass(**kwargs):
            return {
                "success": True,
                "result": "mass_calculated",
                "tool_name": "calculate_mass",
                "execution_time": 0.05
            }

        async def mock_export_step(**kwargs):
            return {
                "success": True,
                "result": "exported_to_step",
                "tool_name": "export_step",
                "execution_time": 0.05
            }

        async def mock_export_pdf(**kwargs):
            return {
                "success": True,
                "result": "exported_to_pdf",
                "tool_name": "export_pdf",
                "execution_time": 0.05
            }

        async def mock_assign_material(**kwargs):
            return {
                "success": True,
                "result": "material_assigned",
                "tool_name": "assign_material",
                "execution_time": 0.05
            }

        async def mock_get_mass_properties(**kwargs):
            return {
                "success": True,
                "result": "mass_properties",
                "tool_name": "get_mass_properties",
                "execution_time": 0.05
            }

        # FIX-02: 添加特征操作需要的mock工具
        async def mock_create_fillet(**kwargs):
            """创建圆角或倒角（FIX-02）"""
            return {
                "success": True,
                "result": "mock_fillet_created",
                "tool_name": "create_fillet",
                "execution_time": 0.05
            }

        async def mock_create_extrude_cut(**kwargs):
            """创建拉伸切除（用于孔等，FIX-02）"""
            return {
                "success": True,
                "result": "mock_extrude_cut_created",
                "tool_name": "create_extrude_cut",
                "execution_time": 0.05
            }

        async def mock_create_linear_pattern(**kwargs):
            """创建线性阵列（FIX-02）"""
            return {
                "success": True,
                "result": "mock_linear_pattern_created",
                "tool_name": "create_linear_pattern",
                "execution_time": 0.05
            }

        # ENH-01: 添加装配体操作的mock工具
        async def mock_create_assembly(**kwargs):
            """创建装配体（ENH-01）"""
            return {
                "success": True,
                "result": "mock_assembly_created",
                "tool_name": "create_assembly",
                "execution_time": 0.1
            }

        async def mock_add_mate(**kwargs):
            """添加配合（ENH-01）"""
            mate_type = kwargs.get("mate_type", "coaxial")
            return {
                "success": True,
                "result": f"mock_mate_added_{mate_type}",
                "tool_name": "add_mate",
                "mate_type": mate_type,
                "execution_time": 0.05
            }

        async def mock_check_interference(**kwargs):
            """检查干涉（ENH-01）"""
            return {
                "success": True,
                "result": "no_interference",
                "tool_name": "check_interference",
                "interference_found": False,
                "execution_time": 0.1
            }

        async def mock_create_exploded_view(**kwargs):
            """创建爆炸视图（ENH-01）"""
            return {
                "success": True,
                "result": "exploded_view_created",
                "tool_name": "create_exploded_view",
                "execution_time": 0.1
            }

        async def mock_check_clearance(**kwargs):
            """检查间隙（ENH-01）"""
            return {
                "success": True,
                "result": "clearance_checked",
                "tool_name": "check_clearance",
                "clearance_value": 1.0,
                "execution_time": 0.1
            }

        async def mock_modify_assembly(**kwargs):
            """修改装配体（ENH-01）"""
            return {
                "success": True,
                "result": "mock_assembly_modified",
                "tool_name": "modify_assembly",
                "execution_time": 0.05
            }

        # ENH-02: 工程图操作工具
        async def mock_create_drawing(**kwargs):
            """创建工程图（ENH-02）"""
            return {
                "success": True,
                "result": "mock_drawing_created",
                "tool_name": "create_drawing",
                "execution_time": 0.1
            }

        async def mock_add_dimensions(**kwargs):
            """添加尺寸标注（ENH-02）"""
            return {
                "success": True,
                "result": "mock_dimensions_added",
                "tool_name": "add_dimensions",
                "execution_time": 0.05
            }

        async def mock_add_annotation(**kwargs):
            """添加注释（ENH-02）"""
            return {
                "success": True,
                "result": "mock_annotation_added",
                "tool_name": "add_annotation",
                "execution_time": 0.05
            }

        async def mock_export_drawing(**kwargs):
            """导出工程图（ENH-02）"""
            format = kwargs.get("format", "pdf")
            return {
                "success": True,
                "result": f"mock_drawing_exported_to_{format}",
                "tool_name": "export_drawing",
                "execution_time": 0.05
            }

        async def mock_modify_drawing(**kwargs):
            """修改工程图（ENH-02）"""
            return {
                "success": True,
                "result": "mock_drawing_modified",
                "tool_name": "modify_drawing",
                "execution_time": 0.05
            }

        # 注册mock工具
        self.executor.register_tool("create_part", mock_create_part)
        self.executor.register_tool("modify_part", mock_modify_part)
        self.executor.register_tool("add_fillet", mock_add_fillet)
        self.executor.register_tool("add_chamfer", mock_add_chamfer)
        # FIX-03: 注册复合操作工具
        self.executor.register_tool("calculate_mass", mock_calculate_mass)
        self.executor.register_tool("export_step", mock_export_step)
        self.executor.register_tool("export_pdf", mock_export_pdf)
        self.executor.register_tool("assign_material", mock_assign_material)
        self.executor.register_tool("get_mass_properties", mock_get_mass_properties)
        # FIX-02: 注册特征操作工具
        self.executor.register_tool("create_fillet", mock_create_fillet)
        self.executor.register_tool("create_extrude_cut", mock_create_extrude_cut)
        self.executor.register_tool("create_linear_pattern", mock_create_linear_pattern)
        # ENH-01: 注册装配体操作工具
        self.executor.register_tool("create_assembly", mock_create_assembly)
        self.executor.register_tool("add_mate", mock_add_mate)
        self.executor.register_tool("check_interference", mock_check_interference)
        self.executor.register_tool("create_exploded_view", mock_create_exploded_view)
        self.executor.register_tool("check_clearance", mock_check_clearance)
        self.executor.register_tool("modify_assembly", mock_modify_assembly)
        # ENH-02: 注册工程图操作工具
        self.executor.register_tool("create_drawing", mock_create_drawing)
        self.executor.register_tool("add_dimensions", mock_add_dimensions)
        self.executor.register_tool("add_annotation", mock_add_annotation)
        self.executor.register_tool("export_drawing", mock_export_drawing)
        self.executor.register_tool("modify_drawing", mock_modify_drawing)

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
        # ENH-07: 根据MCP连接状态确定模式
        mode = "mock"
        if self.use_real_mcp:
            # 尝试连接MCP，如果失败则回退到mock
            if self.executor._mcp_connected:
                mode = "real_solidworks"
            else:
                mode = "mock_with_mcp_fallback"

        result = CoordinatorResult(
            success=False,
            feedback="",
            total_time=0.0,
            mode=mode,
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
                    result.error_message or "无法理解您的设计意图，请提供更清晰的描述",
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

            # FIX-04: 如果是特征操作，添加上下文警告
            if intent_result.object == ObjectType.FEATURE:
                result.feedback += "\n⚠ 警告: 特征操作通常需要现有模型上下文"

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

    def _understand_intent(self, user_input: str, result: CoordinatorResult) -> Optional[Intent]:
        """理解用户意图"""
        if not user_input or not user_input.strip():
            result.error_type = "IntentError"
            return None

        try:
            # 返回Intent对象
            intent_obj = self.intent_engine.understand(user_input)

            # 检查是否理解失败
            # FIX-01: 拒绝两种情况：
            # 1. action=UNKNOWN (验证失败，如无关键词、纯特殊字符等)
            # 2. confidence < 0.2 (极低置信度，如空字符串、单字)
            if intent_obj.action == ActionType.UNKNOWN or intent_obj.confidence < 0.2:
                result.error_type = "IntentError"
                # 从constraints中获取具体的验证原因
                if intent_obj.constraints and len(intent_obj.constraints) > 0:
                    result.error_message = intent_obj.constraints[0]
                else:
                    result.error_message = "无法理解输入"
                return None

            # 保存意图到结果（枚举转字符串）
            action_str = intent_obj.action.value if hasattr(intent_obj.action, 'value') else str(intent_obj.action)
            object_str = intent_obj.object.value if hasattr(intent_obj.object, 'value') else str(intent_obj.object)
            result.intent = f"{action_str}_{object_str}"

            return intent_obj

        except Exception as e:
            result.error_type = "IntentError"
            result.error_message = str(e)
            return None

    def _decompose_tasks(self, intent_obj: Intent, result: CoordinatorResult) -> List[Task]:
        """分解意图为任务"""
        try:
            # Intent对象已经包含action和object（枚举类型）
            # 不需要重新构建，直接使用

            # FIX-03: 使用统一的 decompose 方法（支持复合操作和特征操作）
            tasks = self.decomposer.decompose(intent_obj)

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

    def _validate_results(self, execution_result: ExecutionResult, intent_obj: Intent,
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

            # 将Intent对象转换为字典（验证器可能期望字典格式）
            intent_dict = {
                "action": intent_obj.action.value if hasattr(intent_obj.action, 'value') else intent_obj.action,
                "object": intent_obj.object.value if hasattr(intent_obj.object, 'value') else intent_obj.object,
                "parameters": intent_obj.parameters,
                "confidence": intent_obj.confidence
            }

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

    def _generate_success_feedback(self, intent_obj: Intent, tasks: List[Task],
                                   execution_result: ExecutionResult,
                                   validation_report: ValidationReport) -> str:
        """生成成功反馈"""
        feedback_parts = []

        # 1. 意图确认（从Intent对象获取枚举值）
        action = intent_obj.action.value if hasattr(intent_obj.action, 'value') else str(intent_obj.action)
        obj = intent_obj.object.value if hasattr(intent_obj.action, 'value') else str(intent_obj.object)

        # FIX-03/E2E-09: 如果是CREATE操作，尝试从raw_input或tasks中提取零件类型
        if intent_obj.action == ActionType.CREATE and intent_obj.raw_input:
            # 尝试从raw_input中提取零件类型描述
            part_type_desc = None
            raw_input_lower = intent_obj.raw_input.lower()

            # 检查常见的零件类型关键词
            if any(word in raw_input_lower for word in ['立方体', 'cube', '方块', 'block']):
                part_type_desc = "立方体"
            elif any(word in raw_input_lower for word in ['圆柱', 'cylinder', '圆柱体']):
                part_type_desc = "圆柱"
            elif any(word in raw_input_lower for word in ['球体', 'sphere', '球']):
                part_type_desc = "球体"
            elif any(word in raw_input_lower for word in ['长方体', 'cuboid']):
                part_type_desc = "长方体"

            if part_type_desc:
                feedback_parts.append(f"✓ 已理解您的设计意图: 创建 {part_type_desc}")
            else:
                feedback_parts.append(f"✓ 已理解您的设计意图: {action} {obj}")
        else:
            feedback_parts.append(f"✓ 已理解您的设计意图: {action} {obj}")

        # FIX-06: 如果有尺寸参数，显示尺寸信息
        if "dimensions" in intent_obj.parameters and intent_obj.parameters["dimensions"]:
            dimensions = intent_obj.parameters["dimensions"]
            # 格式化尺寸显示，避免过多小数位
            formatted_dims = [f"{d:.0f}" if d == int(d) else f"{d:.1f}" for d in dimensions]
            feedback_parts.append(f"✓ 尺寸: {formatted_dims[0]} x {formatted_dims[1]} x {formatted_dims[2]} mm")

        # FIX-05: 检查是否是标准件，添加标准件信息
        standard_component = self._identify_standard_component(intent_obj.raw_input)
        if standard_component:
            component_name = standard_component.get("name", "")
            feedback_parts.append(f"✓ 标准件: {component_name}")

        # FIX-03: 显示任务详情（多任务或单个ANALYZE任务）
        show_task_details = execution_result.success_count > 1 or intent_obj.action == ActionType.ANALYZE

        if show_task_details:
            task_descriptions = []
            for r in execution_result.results:
                if r.success:
                    task_desc = self._get_task_description(r.tool_name)
                    task_descriptions.append(task_desc)
            if task_descriptions:
                feedback_parts.append(f"✓ 已完成: {', '.join(task_descriptions)}")

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

    def _get_task_description(self, tool_name: str) -> str:
        """
        获取工具的友好描述（FIX-03）

        Args:
            tool_name: 工具名称

        Returns:
            友好的描述字符串
        """
        descriptions = {
            "create_part": "创建零件",
            "modify_part": "修改零件",
            "calculate_mass": "质量分析",
            "get_mass_properties": "质量分析",
            "export_step": "导出STEP",
            "export_pdf": "导出PDF",
            "assign_material": "设置材料",
            "add_fillet": "添加圆角/倒角",
            "add_chamfer": "添加倒角",
            # FIX-02: 特征操作工具描述
            "create_fillet": "添加圆角/倒角",
            "create_extrude_cut": "创建孔特征",
            "create_linear_pattern": "创建线性阵列"
        }
        return descriptions.get(tool_name, tool_name)

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
        # FIX-01: 使用具体的错误消息而不是通用消息
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

    def _identify_standard_component(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        识别输入是否为标准件（FIX-05）

        Args:
            user_input: 原始用户输入

        Returns:
            标准件信息字典，如果不是标准件则返回None
        """
        if not user_input:
            return None

        # 使用知识库查询标准件
        result = self.knowledge_base.search_standard_component(user_input)

        # 只返回明确找到的标准件
        if result and "name" in result:
            return result

        return None
