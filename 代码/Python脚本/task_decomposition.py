"""
Task Decomposition Module

将用户意图分解为可执行的 SolidWorks API 任务序列。
"""

from typing import List
from schemas import Intent, Task, ActionType, ObjectType
import uuid


class TaskDecomposer:
    """任务分解器 - 将意图转换为任务序列"""

    def __init__(self):
        """初始化任务分解器"""
        self._task_counter = 0

    def decompose(self, intent: Intent) -> List[Task]:
        """
        将意图分解为任务列表

        Args:
            intent: 用户意图

        Returns:
            任务列表（按依赖顺序排列）

        Raises:
            ValueError: 当意图不支持或参数无效时
        """
        self._task_counter = 0

        # 根据动作类型分发
        if intent.action == ActionType.CREATE:
            return self._decompose_create(intent)
        elif intent.action == ActionType.MODIFY:
            return self._decompose_modify(intent)
        elif intent.action == ActionType.ANALYZE:
            return self._decompose_analyze(intent)
        elif intent.action == ActionType.EXPORT:
            return self._decompose_export(intent)
        else:
            raise ValueError(f"Unknown action type: {intent.action}")

    def _create_task(self, tool: str, description: str, parameters: dict, dependencies: List[str] = None) -> Task:
        """创建任务对象"""
        self._task_counter += 1
        return Task(
            id=str(uuid.uuid4()),
            tool=tool,
            description=description,
            parameters=parameters,
            dependencies=dependencies or []
        )

    def _decompose_create(self, intent: Intent) -> List[Task]:
        """分解 CREATE 意图"""
        if intent.object != ObjectType.PART:
            raise ValueError(f"Unknown entity type: {intent.object}")

        params = intent.parameters

        # 验证必需参数
        if "name" not in params:
            raise ValueError("Missing required parameter: name")
        if "type" not in params:
            raise ValueError("Missing required parameter: type")

        part_type = params["type"]

        # 创建零件任务
        create_part_task = self._create_task(
            tool="create_part",
            description=f"Create part: {params['name']}",
            parameters={"name": params["name"]}
        )

        # 创建草图任务
        sketch_plane = params.get("plane", "Front")
        create_sketch_task = self._create_task(
            tool="create_sketch",
            description=f"Create sketch on {sketch_plane} plane",
            parameters={"plane": sketch_plane},
            dependencies=[create_part_task.id]
        )

        # 根据类型创建几何体
        if part_type == "cube":
            self._validate_cube_params(params)
            create_geometry_task = self._create_task(
                tool="create_rectangle",
                description=f"Create rectangle {params['width']}x{params['height']}",
                parameters={
                    "width": params["width"],
                    "height": params["height"]
                },
                dependencies=[create_sketch_task.id]
            )
        elif part_type == "cylinder":
            self._validate_cylinder_params(params)
            create_geometry_task = self._create_task(
                tool="create_circle",
                description=f"Create circle diameter={params['diameter']}",
                parameters={"diameter": params["diameter"]},
                dependencies=[create_sketch_task.id]
            )
        else:
            raise ValueError(f"Unknown part type: {part_type}")

        # 创建拉伸任务
        # For cylinder, use 'height' as depth; for cube, use 'depth'
        if part_type == "cylinder":
            depth = params.get("height")
        else:
            depth = params.get("depth")

        if depth is None:
            raise ValueError(f"Missing required parameter: {'height' if part_type == 'cylinder' else 'depth'}")

        self._validate_positive_dimension(depth, "depth")

        extrude_task = self._create_task(
            tool="extrude_boss",
            description=f"Extrude to depth={depth}",
            parameters={
                "depth": depth,
                "direction": params.get("direction", "blind")
            },
            dependencies=[create_geometry_task.id]
        )

        return [create_part_task, create_sketch_task, create_geometry_task, extrude_task]

    def _decompose_modify(self, intent: Intent) -> List[Task]:
        """分解 MODIFY 意图"""
        params = intent.parameters

        # 判断修改类型
        if "feature" in params and "dimension" in params:
            # 修改尺寸
            self._validate_modify_params(params, ["feature", "dimension", "value"])
            return [self._create_task(
                tool="modify_dimension",
                description=f"Modify dimension {params['dimension']} in {params['feature']}",
                parameters={
                    "feature": params["feature"],
                    "dimension": params["dimension"],
                    "value": params["value"]
                }
            )]
        elif "name" in params:
            # 修改特征参数
            self._validate_modify_params(params, ["name"])
            return [self._create_task(
                tool="modify_feature",
                description=f"Modify feature {params['name']}",
                parameters={k: v for k, v in params.items() if k != "target"}
            )]
        else:
            raise ValueError("Missing required parameter: need 'feature'&'dimension' or 'name'")

    def _decompose_analyze(self, intent: Intent) -> List[Task]:
        """分解 ANALYZE 意图"""
        params = intent.parameters

        # 检查是否批量分析
        if "metrics" in params:
            metrics = params["metrics"]
            tasks = []
            for metric in metrics:
                task = self._create_task_for_metric(metric, params)
                tasks.append(task)
            return tasks
        else:
            # 单个分析
            metric = params.get("metric", "volume")
            return [self._create_task_for_metric(metric, params)]

    def _create_task_for_metric(self, metric: str, params: dict) -> Task:
        """为特定指标创建分析任务"""
        if metric == "volume" or metric == "mass":
            return self._create_task(
                tool="get_mass_properties",
                description=f"Get mass properties for {metric}",
                parameters={}
            )
        elif metric == "area":
            return self._create_task(
                tool="get_surface_area",
                description="Get surface area",
                parameters={}
            )
        elif metric == "distance":
            # Distance requires entity1 and entity2 in params
            entity1 = params.get("entity1")
            entity2 = params.get("entity2")
            if not entity1 or not entity2:
                raise ValueError("Missing required parameters for distance: entity1, entity2")
            return self._create_task(
                tool="measure_distance",
                description=f"Measure distance between {entity1} and {entity2}",
                parameters={
                    "entity1": entity1,
                    "entity2": entity2
                }
            )
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def _decompose_export(self, intent: Intent) -> List[Task]:
        """分解 EXPORT 意图"""
        params = intent.parameters

        self._validate_export_params(params)

        if intent.object == ObjectType.PART:
            return [self._create_task(
                tool="export_file",
                description=f"Export part to {params['format']}",
                parameters={
                    "format": params["format"],
                    "filepath": params["filepath"]
                }
            )]
        elif intent.object == ObjectType.DRAWING:
            return [self._create_task(
                tool="export_drawing",
                description=f"Export drawing to {params['format']}",
                parameters={
                    "format": params["format"],
                    "filepath": params["filepath"]
                }
            )]
        else:
            raise ValueError(f"Cannot export object type: {intent.object}")

    # 参数验证方法

    def _validate_cube_params(self, params: dict):
        """验证立方体参数"""
        required = ["width", "height", "depth"]
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
            self._validate_positive_dimension(params[param], param)

    def _validate_cylinder_params(self, params: dict):
        """验证圆柱参数"""
        if "diameter" not in params:
            raise ValueError("Missing required parameter: diameter")
        self._validate_positive_dimension(params["diameter"], "diameter")

    def _validate_modify_params(self, params: dict, required: List[str]):
        """验证修改参数"""
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")

    def _validate_analyze_params(self, params: dict, required: List[str]):
        """验证分析参数"""
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")

    def _validate_export_params(self, params: dict):
        """验证导出参数"""
        required = ["format", "filepath"]
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")

    def _validate_positive_dimension(self, value: float, name: str):
        """验证尺寸为正数"""
        if value is None or value <= 0:
            raise ValueError(f"Dimension must be positive: {name}={value}")
