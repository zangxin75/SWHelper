"""
Task Decomposer Module

将结构化意图分解为可执行的任务序列
"""

from typing import List, Dict, Any
from schemas import Intent, Task


class TaskDecomposer:
    """
    任务分解器

    功能：
    - 将结构化意图分解为工具任务
    - 处理任务依赖关系
    - 生成任务序列
    """

    def __init__(self):
        """初始化任务分解器"""
        # 工具映射表
        self._action_tool_mapping = {
            "create": "create_part",
            "modify": "modify_part",
            "analyze": "analyze_part",
            "export": "export_part"
        }

    def decompose(self, intent: Intent) -> List[Task]:
        """
        分解意图为任务序列

        Args:
            intent: 结构化意图

        Returns:
            任务列表
        """
        if not intent or intent.action not in self._action_tool_mapping:
            return []

        # 获取对应的工具
        tool_name = self._action_tool_mapping.get(intent.action.value)

        # 构建任务
        task = Task(
            id=f"{intent.action.value}_1",
            tool=tool_name,
            description=f"{intent.action.value} {intent.object.value}",
            parameters=intent.parameters,
            dependencies=[]
        )

        return [task]

    def decompose_complex(self, intent: Intent) -> List[Task]:
        """
        分解复杂意图为多任务序列

        Args:
            intent: 结构化意图

        Returns:
            任务列表（可能有多个任务和依赖关系）
        """
        tasks = []

        # 检查是否需要多个任务
        # 例如："创建立方体然后倒角" 需要两个任务

        parameters = intent.parameters or {}

        # 第一个任务：创建基础特征
        create_task = Task(
            id="create_1",
            tool="create_part",
            description=f"create {intent.object.value}",
            parameters=parameters,
            dependencies=[]
        )
        tasks.append(create_task)

        # 检查是否有额外的特征需求
        if "fillet_radius" in parameters:
            # 第二个任务：添加圆角
            fillet_task = Task(
                id="fillet_1",
                tool="add_fillet",
                description="add fillet to edges",
                parameters={"radius": parameters["fillet_radius"]},
                dependencies=["create_1"]
            )
            tasks.append(fillet_task)

        if "chamfer_distance" in parameters:
            # 第二个任务：添加倒角
            chamfer_task = Task(
                id="chamfer_1",
                tool="add_chamfer",
                description="add chamfer to edges",
                parameters={"distance": parameters["chamfer_distance"]},
                dependencies=["create_1"]
            )
            tasks.append(chamfer_task)

        return tasks
