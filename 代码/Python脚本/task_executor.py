"""
Task Executor Module

执行任务序列，处理依赖关系，支持并行执行和错误恢复。

ENH-07: 添加真实MCP集成支持
"""

import asyncio
import time
from typing import List, Dict, Set, Any, Optional
from collections import defaultdict, deque
from loguru import logger

from schemas import Task, ToolResult, ExecutionResult

# ENH-07: MCP客户端导入
try:
    from mcp_client import MCPClient, MCP_AVAILABLE
except ImportError:
    MCPClient = None
    MCP_AVAILABLE = False


class TaskExecutor:
    """
    任务执行器

    功能：
    - 解析任务依赖关系
    - 并行执行独立任务
    - 串行执行有依赖的任务
    - 错误处理和重试
    - 执行时间跟踪
    - ENH-07: 真实MCP工具执行
    """

    def __init__(self, use_real_mcp: bool = False, mcp_config: Optional[Dict] = None):
        """
        初始化任务执行器

        Args:
            use_real_mcp: 是否使用真实MCP Server (ENH-07)
            mcp_config: MCP配置参数
        """
        self._tool_registry = {}  # 工具注册表，由外部注入

        # ENH-07: MCP模式配置
        self.use_real_mcp = use_real_mcp
        self.mcp_config = mcp_config or {}
        self._mcp_client: Optional[MCPClient] = None
        self._mcp_connected = False

        # 工具名称映射（mock -> MCP）
        # 更新: 使用sw_create_document统一创建所有文档类型
        self._tool_mapping = {
            # 文档创建 - 100%支持
            "create_part": "sw_create_document",
            "create_assembly": "sw_create_document",
            "create_drawing": "sw_create_document",
            # 其他工具（暂时保留映射）
            "add_dimensions": "sw_add_dimensions",
            "add_annotation": "sw_add_annotation",
            "export_drawing": "sw_export_drawing",
            "modify_part": "sw_modify_feature",
            "add_fillet": "sw_add_fillet",
            "add_chamfer": "sw_add_chamfer",
            "create_extrude_cut": "sw_create_extrude_cut",
            "create_linear_pattern": "sw_create_linear_pattern",
            "add_mate": "sw_add_mate",
            "check_interference": "sw_check_interference",
            "create_exploded_view": "sw_create_exploded_view",
            "check_clearance": "sw_check_clearance",
            "modify_assembly": "sw_modify_assembly",
            "assign_material": "sw_assign_material",
            "calculate_mass": "sw_calculate_mass",
            "get_mass_properties": "sw_get_mass_properties",
            "export_step": "sw_export_step",
            "export_pdf": "sw_export_pdf",
        }

        # 文档类型映射
        self._doc_type_mapping = {
            "create_part": "part",
            "create_assembly": "assembly",
            "create_drawing": "drawing",
        }

    def register_tool(self, name: str, func):
        """
        注册工具函数

        Args:
            name: 工具名称
            func: 异步工具函数
        """
        self._tool_registry[name] = func

    async def _connect_mcp(self) -> bool:
        """
        ENH-07: 连接到MCP服务器

        Returns:
            连接是否成功
        """
        if not self.use_real_mcp or not MCP_AVAILABLE:
            logger.debug("MCP mode disabled or MCP SDK not available")
            return False

        if self._mcp_connected:
            logger.debug("MCP already connected")
            return True

        try:
            # 创建MCP客户端
            server_command = self.mcp_config.get("command", "python")
            server_args = self.mcp_config.get("args", ["-m", "solidworks_mcp"])
            timeout = self.mcp_config.get("timeout", 30.0)

            self._mcp_client = MCPClient(
                server_command=server_command,
                server_args=server_args,
                timeout=timeout
            )

            # 尝试连接
            logger.info(f"Attempting to connect to MCP server: {server_command} {' '.join(server_args)}")
            success = await self._mcp_client.connect()

            if success:
                self._mcp_connected = True
                tool_count = self._mcp_client.get_tool_count()
                logger.info(f"MCP connection established. {tool_count} tools available.")
            else:
                logger.warning("MCP connection failed, will use mock mode")

            return success

        except Exception as e:
            logger.error(f"MCP connection error: {e}")
            self._mcp_connected = False
            return False

    async def _disconnect_mcp(self):
        """ENH-07: 断开MCP连接"""
        if self._mcp_client and self._mcp_connected:
            try:
                await self._mcp_client.disconnect()
                logger.info("MCP connection closed")
            except Exception as e:
                logger.error(f"Error disconnecting MCP: {e}")
            finally:
                self._mcp_connected = False

    async def execute(self, tasks: List[Task]) -> ExecutionResult:
        """
        执行任务序列

        ENH-07: 如果use_real_mcp=True，尝试连接MCP服务器

        Args:
            tasks: 任务列表

        Returns:
            ExecutionResult: 执行结果

        Raises:
            ValueError: 如果检测到循环依赖
        """
        if not tasks:
            return ExecutionResult(
                results=[],
                failed_tasks=[],
                total_time=0.0,
                success_count=0,
                failure_count=0
            )

        # ENH-07: 尝试连接MCP（如果启用）
        if self.use_real_mcp:
            await self._connect_mcp()

        start_time = time.perf_counter()

        # 1. 构建任务索引
        task_map = {task.id: task for task in tasks}

        # 2. 检测循环依赖
        self._detect_circular_dependencies(tasks, task_map)

        # 3. 解析依赖关系，分层执行
        results = []
        failed_tasks = []
        executed = set()  # 已执行的任务

        # 使用拓扑排序分层
        layers = self._topological_sort_with_layers(tasks, task_map)

        # 按层执行任务
        for layer in layers:
            # 过滤掉依赖失败的任务
            executable_tasks = []
            for task_id in layer:
                task = task_map[task_id]

                # 检查依赖是否都成功
                deps_satisfied = True
                for dep_id in task.dependencies:
                    if dep_id in failed_tasks:
                        deps_satisfied = False
                        break

                if deps_satisfied:
                    executable_tasks.append(task)
                else:
                    # 依赖失败，跳过此任务
                    failed_tasks.append(task_id)
                    executed.add(task_id)

            # 并行执行当前层的所有任务
            if executable_tasks:
                layer_results = await asyncio.gather(
                    *[self._execute_task(task, task_map) for task in executable_tasks],
                    return_exceptions=True
                )

                # 处理结果
                for task, result in zip(executable_tasks, layer_results):
                    if isinstance(result, Exception):
                        # 任务执行失败
                        failed_tasks.append(task.id)
                        results.append(ToolResult(
                            success=False,
                            tool_name=task.tool,
                            error=str(result),
                            execution_time=0.0,
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                    else:
                        # 任务成功
                        if not result.success:
                            failed_tasks.append(task.id)
                        results.append(result)

                    executed.add(task.id)

        # 等待所有异步任务完成
        await asyncio.sleep(0)

        total_time = time.perf_counter() - start_time

        # 统计成功/失败数量
        success_count = sum(1 for r in results if r.success)
        failure_count = len(results) - success_count

        return ExecutionResult(
            results=results,
            failed_tasks=failed_tasks,
            total_time=total_time,
            success_count=success_count,
            failure_count=failure_count
        )

    def _detect_circular_dependencies(self, tasks: List[Task], task_map: Dict[str, Task]):
        """
        检测循环依赖（使用DFS）

        Args:
            tasks: 任务列表
            task_map: 任务ID到任务的映射

        Raises:
            ValueError: 如果检测到循环依赖
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {task.id: WHITE for task in tasks}

        def dfs(task_id: str, path: Set[str]):
            if color[task_id] == GRAY:
                # 找到环
                cycle = " -> ".join(path)
                raise ValueError(f"Circular dependency detected: {cycle}")

            if color[task_id] == BLACK:
                return

            color[task_id] = GRAY
            path.add(task_id)

            if task_id in task_map:
                for dep_id in task_map[task_id].dependencies:
                    if dep_id in color:  # 只检查已知任务
                        dfs(dep_id, path.copy())

            color[task_id] = BLACK

        for task in tasks:
            if color[task.id] == WHITE:
                dfs(task.id, set())

    def _topological_sort_with_layers(self, tasks: List[Task], task_map: Dict[str, Task]) -> List[List[str]]:
        """
        拓扑排序并分层（Kahn's algorithm）

        返回的每一层可以并行执行

        Args:
            tasks: 任务列表
            task_map: 任务ID到任务的映射

        Returns:
            List[List[str]]: 分层的任务ID列表
        """
        # 计算入度
        in_degree = {task.id: 0 for task in tasks}
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in in_degree:
                    in_degree[task.id] += 1

        # 初始化队列（入度为0的任务）
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        layers = []

        while queue:
            current_layer = []
            next_queue = deque()

            # 处理当前层的所有节点
            while queue:
                task_id = queue.popleft()
                current_layer.append(task_id)

                # 减少依赖此任务的节点的入度
                for task in tasks:
                    if task_id in task.dependencies:
                        in_degree[task.id] -= 1
                        if in_degree[task.id] == 0:
                            next_queue.append(task.id)

            layers.append(current_layer)
            queue = next_queue

        return layers

    async def _execute_mcp_tool(self, task: Task) -> ToolResult:
        """
        ENH-07: 执行单个MCP工具

        Args:
            task: 要执行的任务

        Returns:
            ToolResult: 执行结果
        """
        start_time = time.perf_counter()

        # 检查MCP连接
        if not self._mcp_connected or not self._mcp_client:
            return ToolResult(
                success=False,
                tool_name=task.tool,
                error="MCP not connected. Falling back to mock mode",
                execution_time=time.perf_counter() - start_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )

        # 映射工具名称
        mcp_tool_name = self._tool_mapping.get(task.tool, task.tool)

        # 特殊处理: 文档创建工具需要转换参数
        mcp_args = task.parameters.copy()
        if task.tool in self._doc_type_mapping:
            # 转换为sw_create_document的参数格式
            mcp_args = {
                "doc_type": self._doc_type_mapping[task.tool],
                "template": task.parameters.get("template")  # 可选的模板参数
            }
            logger.debug(f"Mapped {task.tool} to sw_create_document with args: {mcp_args}")

        try:
            logger.debug(f"Calling MCP tool: {mcp_tool_name} with args: {mcp_args}")

            # 调用MCP工具
            mcp_result = await self._mcp_client.call_tool(
                tool_name=mcp_tool_name,
                arguments=mcp_args
            )

            execution_time = time.perf_counter() - start_time

            # 解析MCP结果
            # MCP返回格式: {"success": bool, "result": ..., "error": ...}
            if isinstance(mcp_result, dict):
                if mcp_result.get("success"):
                    return ToolResult(
                        success=True,
                        tool_name=task.tool,
                        result=mcp_result.get("result"),
                        execution_time=execution_time,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
                else:
                    return ToolResult(
                        success=False,
                        tool_name=task.tool,
                        error=mcp_result.get("error", "Unknown MCP error"),
                        execution_time=execution_time,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
            else:
                # 非字典结果，包装为成功
                return ToolResult(
                    success=True,
                    tool_name=task.tool,
                    result=mcp_result,
                    execution_time=execution_time,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )

        except TimeoutError as e:
            execution_time = time.perf_counter() - start_time
            logger.error(f"MCP tool timeout: {e}")
            return ToolResult(
                success=False,
                tool_name=task.tool,
                error=f"MCP tool timeout: {str(e)}",
                execution_time=execution_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )

        except Exception as e:
            execution_time = time.perf_counter() - start_time
            logger.error(f"MCP tool error: {e}")
            return ToolResult(
                success=False,
                tool_name=task.tool,
                error=f"MCP tool error: {str(e)}",
                execution_time=execution_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )

    async def _execute_task(self, task: Task, task_map: Dict[str, Task]) -> ToolResult:
        """
        执行单个任务（带重试）

        Args:
            task: 要执行的任务
            task_map: 任务ID到任务的映射

        Returns:
            ToolResult: 执行结果
        """
        start_time = time.perf_counter()

        # 检查依赖是否存在
        for dep_id in task.dependencies:
            if dep_id not in task_map:
                return ToolResult(
                    success=False,
                    tool_name=task.tool,
                    error=f"Dependency task '{dep_id}' not found",
                    execution_time=0.0,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )

        # 检查工具是否注册
        if task.tool not in self._tool_registry:
            return ToolResult(
                success=False,
                tool_name=task.tool,
                error=f"Tool '{task.tool}' not found in registry",
                execution_time=time.perf_counter() - start_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )

        # ENH-07: 路由到MCP或Mock执行
        if self._mcp_connected and self.use_real_mcp:
            # 使用真实MCP工具
            logger.debug(f"Executing {task.tool} via MCP")
            return await self._execute_mcp_tool(task)
        else:
            # 使用Mock工具
            logger.debug(f"Executing {task.tool} via Mock")
            tool_func = self._tool_registry[task.tool]
            last_error = None

        for attempt in range(task.max_retries + 1):
            try:
                result = await tool_func(**task.parameters)
                execution_time = time.perf_counter() - start_time

                return ToolResult(
                    success=True,
                    tool_name=task.tool,
                    result=result,
                    execution_time=execution_time,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception as e:
                last_error = e
                if attempt < task.max_retries:
                    # 重试前等待一小段时间
                    await asyncio.sleep(0.01 * (attempt + 1))
                continue

        # 所有重试都失败
        execution_time = time.perf_counter() - start_time
        return ToolResult(
            success=False,
            tool_name=task.tool,
            error=f"Execution failed after {task.max_retries + 1} attempts: {str(last_error)}",
            execution_time=execution_time,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
