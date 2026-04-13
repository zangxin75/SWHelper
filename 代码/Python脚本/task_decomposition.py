"""
Task Decomposition Module

将用户意图分解为可执行的 SolidWorks API 任务序列。
"""

from typing import List, Optional
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

        # FIX-03: 检测复合操作（创建+分析、创建+导出等）
        compound_operations = self._detect_compound_operations(intent)
        if compound_operations:
            return self._decompose_compound(intent, compound_operations)

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
        params = intent.parameters or {}

        # ENH-01: 支持装配体创建
        if intent.object == ObjectType.ASSEMBLY:
            return self._decompose_create_assembly(intent)

        # ENH-02: 支持工程图创建
        if intent.object == ObjectType.DRAWING:
            return self._decompose_create_drawing(intent)

        if intent.object != ObjectType.PART:
            raise ValueError(f"Unknown entity type: {intent.object}")

        # FIX-03: 为缺失参数提供默认值（支持简化的创建意图）
        if "name" not in params:
            params["name"] = "part"
        if "type" not in params:
            # 尝试从raw_input中提取类型
            if hasattr(intent, 'raw_input') and intent.raw_input:
                params["type"] = self._extract_part_type(intent.raw_input)
            else:
                params["type"] = "cube"  # 默认类型

        part_type = params["type"]

        # FIX-03: 为缺失的尺寸参数提供默认值
        if part_type == "cube":
            if "width" not in params:
                params["width"] = 100.0
            if "height" not in params:
                params["height"] = 100.0
            if "depth" not in params:
                params["depth"] = 100.0
        elif part_type == "cylinder":
            if "diameter" not in params:
                params["diameter"] = 50.0
            if "height" not in params:
                params["height"] = 100.0

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

        # FIX-02: 支持在现有模型上添加特征
        if intent.object == ObjectType.FEATURE:
            return self._decompose_add_feature(params)

        # ENH-01: 支持装配体修改（添加配合、爆炸视图等）
        if intent.object == ObjectType.ASSEMBLY:
            return self._decompose_modify_assembly(intent)

        # ENH-02: 支持工程图修改（添加尺寸、注释等）
        if intent.object == ObjectType.DRAWING:
            return self._decompose_modify_drawing(intent)

        # 原有的PART修改逻辑
        if intent.object != ObjectType.PART:
            raise ValueError(f"Cannot modify object type: {intent.object}")

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

    def _decompose_add_feature(self, params: dict) -> List[Task]:
        """
        分解添加特征的操作（FIX-02）

        支持的特征类型：
        - chamfer（倒角）
        - fillet（圆角）
        - hole（孔）
        - pattern（阵列）

        支持多特征：如果params中有"features"列表，会为每个特征创建一个任务
        """
        # 检查是否是多特征
        if "features" in params:
            features = params["features"]
            tasks = []
            for feature_info in features:
                task = self._create_single_feature_task(feature_info)
                if task:
                    tasks.append(task)
            return tasks

        # 单特征情况
        return [self._create_single_feature_task(params)]

    def _create_single_feature_task(self, feature_info: dict) -> Optional[Task]:
        """为单个特征创建任务"""
        feature_type = feature_info.get("feature_type")

        if feature_type == "chamfer":
            # 添加倒角
            distance = feature_info.get("distance", 5.0)  # 默认5mm
            return self._create_task(
                tool="create_fillet",  # 倒角和圆角可能使用同一个工具，或使用create_chamfer
                description=f"Create {distance}mm chamfer",
                parameters={"size": distance}
            )

        elif feature_type == "fillet":
            # 添加圆角
            radius = feature_info.get("radius", 5.0)  # 默认5mm
            return self._create_task(
                tool="create_fillet",
                description=f"Create {radius}mm fillet",
                parameters={"radius": radius}
            )

        elif feature_type == "hole":
            # 添加孔
            diameter = feature_info.get("diameter", 10.0)  # 默认10mm
            return self._create_task(
                tool="create_extrude_cut",
                description=f"Create {diameter}mm hole",
                parameters={"diameter": diameter}
            )

        elif feature_type == "pattern":
            # 添加阵列
            spacing = feature_info.get("spacing", 20.0)  # 默认20mm
            count = feature_info.get("count", 5)  # 默认5个
            return self._create_task(
                tool="create_linear_pattern",
                description=f"Create linear pattern: spacing={spacing}mm, count={count}",
                parameters={"spacing": spacing, "count": count}
            )

        else:
            raise ValueError(f"Unknown feature type: {feature_type}")

    def _decompose_analyze(self, intent: Intent) -> List[Task]:
        """分解 ANALYZE 意图"""
        params = intent.parameters

        # ENH-01: 支持装配体分析（干涉检查等）
        if intent.object == ObjectType.ASSEMBLY:
            return self._decompose_analyze_assembly(intent)

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

        # ENH-02: 为DRAWING导出提供默认filepath（如果缺失）
        if intent.object == ObjectType.DRAWING and "filepath" not in params:
            params = dict(params)  # 创建副本避免修改原参数
            format_type = params.get("format", "pdf")
            params["filepath"] = f"drawing_export.{format_type}"

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
                tool="export_drawing_pdf",
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

    # FIX-03: 复合操作支持

    def _detect_compound_operations(self, intent: Intent) -> List[str]:
        """
        检测复合操作（FIX-03）

        支持的复合操作类型：
        - create + analyze（创建+分析）
        - create + export（创建+导出）
        - create + assign_material（创建+设置材料）
        - create + analyze + export（创建+分析+导出）

        对于简化的意图（如"创建方块"），也会返回operations列表以使用简化逻辑。

        ENH-01: 装配体不使用复合操作逻辑，因为装配体的分解逻辑更加复杂

        Returns:
            操作类型列表，如["create", "analyze"]
        """
        import re

        # ENH-01: 装配体不使用复合操作逻辑
        if intent.object == ObjectType.ASSEMBLY:
            return []

        raw_input = intent.raw_input if hasattr(intent, 'raw_input') and intent.raw_input else ""

        if not raw_input:
            return []

        operations = []

        # 检测连接词
        has_and = "并" in raw_input
        has_comma = "，" in raw_input or "," in raw_input

        # 检测各个操作类型
        has_create = intent.action == ActionType.CREATE
        has_analyze = re.search(r'分析|计算|测量|analyze', raw_input, re.IGNORECASE)
        has_export = re.search(r'导出|保存|输出|export', raw_input, re.IGNORECASE)
        has_material = re.search(r'材料|material', raw_input, re.IGNORECASE)

        # 根据连接词和操作类型确定是否为复合操作
        if has_and or has_comma:
            # 明确的复合操作
            if has_create:
                operations.append("create")
            if has_analyze:
                operations.append("analyze")
            if has_export:
                operations.append("export")
            if has_material:
                operations.append("assign_material")
        elif has_create and (has_analyze or has_export or has_material):
            # 隐式连接（无连接词但有多个操作）
            operations.append("create")
            if has_analyze:
                operations.append("analyze")
            if has_export:
                operations.append("export")
            if has_material:
                operations.append("assign_material")
        elif has_create:
            # FIX-03/ENH-01: 单一创建操作的判断逻辑
            # 如果有完整的参数（type + dimensions），使用正常的创建流程（4个任务）
            # 如果没有完整参数，使用简化的创建逻辑（1个任务）
            params = intent.parameters or {}

            # 检查是否有完整的创建参数
            part_type = params.get("type")
            has_complete_params = False

            if part_type == "cube":
                has_complete_params = all(k in params for k in ["width", "height", "depth"])
            elif part_type == "cylinder":
                has_complete_params = all(k in params for k in ["diameter", "height"])

            # 如果没有完整参数，使用简化逻辑
            if not has_complete_params:
                operations.append("create")

        # 返回操作列表（包括单一操作的简化逻辑）
        return operations

    def _decompose_compound(self, intent: Intent, operations: List[str]) -> List[Task]:
        """
        分解复合操作为任务列表（FIX-03）

        Args:
            intent: 原始意图
            operations: 操作类型列表，如["create", "analyze"]

        Returns:
            任务列表
        """
        tasks = []
        dependencies = []

        raw_input = intent.raw_input if hasattr(intent, 'raw_input') and intent.raw_input else ""

        # 处理每个操作
        for i, op in enumerate(operations):
            if op == "create":
                # 创建操作：使用简化的创建任务（FIX-03）
                # 检查对象类型是否支持简化创建逻辑
                if intent.object == ObjectType.ASSEMBLY:
                    # 装配体的创建逻辑
                    return self._decompose_create_assembly(intent)
                elif intent.object == ObjectType.DRAWING:
                    # ENH-02: 工程图的创建逻辑
                    return self._decompose_create_drawing(intent)
                elif intent.object not in [ObjectType.PART, ObjectType.UNKNOWN]:
                    # 其他对象类型（FEATURE, SKETCH）不支持简化创建逻辑
                    raise ValueError(f"Unknown entity type: {intent.object}")

                # 从raw_input中提取零件类型
                part_type = self._extract_part_type(raw_input)

                # ENH-01: 检查是否有基本的零件类型参数
                params = intent.parameters or {}
                provided_type = params.get("type")

                # 如果提供了类型但参数不完整，验证所需参数
                if provided_type:
                    if provided_type == "cube":
                        required_params = ["width", "height", "depth"]
                        if not all(k in params for k in required_params):
                            raise ValueError(f"Missing required parameters for cube: {required_params}")
                    elif provided_type == "cylinder":
                        required_params = ["diameter", "height"]
                        if not all(k in params for k in required_params):
                            raise ValueError(f"Missing required parameters for cylinder: {required_params}")

                create_task = self._create_task(
                    tool="create_part",
                    description=f"Create {part_type}",
                    parameters={"type": part_type, "name": f"part_{part_type}"}
                )
                tasks.append(create_task)
                dependencies.append(create_task.id)

            elif op == "analyze":
                # 分析操作：创建质量分析任务
                analyze_task = self._create_task(
                    tool="calculate_mass",
                    description="Calculate mass properties",
                    parameters={},
                    dependencies=dependencies.copy() if dependencies else []
                )
                tasks.append(analyze_task)
                dependencies.append(analyze_task.id)

            elif op == "export":
                # 导出操作：从raw_input中提取导出格式
                export_format = self._extract_export_format(raw_input)
                export_task = self._create_task(
                    tool=f"export_{export_format}",
                    description=f"Export to {export_format}",
                    parameters={"format": export_format, "filepath": f"output.{export_format}"},
                    dependencies=dependencies.copy() if dependencies else []
                )
                tasks.append(export_task)
                dependencies.append(export_task.id)

            elif op == "assign_material":
                # 设置材料操作：从raw_input中提取材料
                material = self._extract_material(raw_input)
                material_task = self._create_task(
                    tool="assign_material",
                    description=f"Assign material: {material}",
                    parameters={"material": material},
                    dependencies=dependencies.copy() if dependencies else []
                )
                tasks.append(material_task)
                dependencies.append(material_task.id)

        return tasks

    def _extract_part_type(self, text: str) -> str:
        """从文本中提取零件类型"""
        import re

        if re.search(r'方块|立方体|长方体', text, re.IGNORECASE):
            return "cube"
        elif re.search(r'圆柱|圆柱体', text, re.IGNORECASE):
            return "cylinder"
        elif re.search(r'球体|球', text, re.IGNORECASE):
            return "sphere"
        else:
            return "part"  # 默认类型

    def _extract_export_format(self, text: str) -> str:
        """从文本中提取导出格式"""
        import re

        # 常见格式
        if re.search(r'STEP|step', text, re.IGNORECASE):
            return "step"
        elif re.search(r'PDF|pdf', text, re.IGNORECASE):
            return "pdf"
        elif re.search(r'STL|stl', text, re.IGNORECASE):
            return "stl"
        elif re.search(r'IGES|iges', text, re.IGNORECASE):
            return "iges"
        else:
            return "step"  # 默认格式

    def _extract_material(self, text: str) -> str:
        """从文本中提取材料"""
        import re

        # 常见材料
        if re.search(r'铝|铝合金', text, re.IGNORECASE):
            return "铝合金_6061"
        elif re.search(r'钢|钢材', text, re.IGNORECASE):
            return "钢_普通"
        elif re.search(r'不锈钢', text, re.IGNORECASE):
            return "不锈钢_304"
        elif re.search(r'铁|铸铁', text, re.IGNORECASE):
            return "铁_铸铁"
        elif re.search(r'塑料|ABS', text, re.IGNORECASE):
            return "ABS塑料"
        else:
            return "铝合金_6061"  # 默认材料

    # ==================== ENH-02: 工程图支持 ====================

    def _decompose_create_drawing(self, intent: Intent) -> List[Task]:
        """
        分解创建工程图的意图（ENH-02）

        支持参数：
        - view_count: 视图数量
        - sheet_format: 图纸格式（A0-A4）
        - scale: 比例（如"1:2"）
        """
        params = intent.parameters or {}
        tasks = []

        # 为缺失参数提供默认值
        if "view_count" not in params:
            params["view_count"] = 3  # 默认3个视图
        if "sheet_format" not in params:
            params["sheet_format"] = "A3"  # 默认A3图纸
        if "scale" not in params:
            params["scale"] = "1:1"  # 默认比例1:1

        # 创建工程图任务
        drawing_task = self._create_task(
            tool="create_drawing",
            description=f"Create drawing with {params['view_count']} views on {params['sheet_format']} sheet",
            parameters={
                "view_count": params["view_count"],
                "sheet_format": params["sheet_format"],
                "scale": params["scale"]
            }
        )
        tasks.append(drawing_task)

        return tasks

    # ==================== ENH-01: 装配体支持 ====================

    def _decompose_create_assembly(self, intent: Intent) -> List[Task]:
        """
        分解创建装配体的意图（ENH-01）

        根据component_count参数决定是否创建零件任务：
        - 如果有component_count参数，先创建零件，再创建装配体
        - 如果是子装配体，只创建装配体
        """
        params = intent.parameters or {}
        tasks = []
        dependencies = []

        # 检查是否是子装配体
        is_subassembly = params.get("is_subassembly", False)
        component_count = params.get("component_count")

        # 如果有组件数量，先创建零件任务
        if component_count and not is_subassembly:
            for i in range(component_count):
                part_task = self._create_task(
                    tool="create_part",
                    description=f"Create component part {i+1}",
                    parameters={"name": f"component_{i+1}"}
                )
                tasks.append(part_task)
                dependencies.append(part_task.id)

        # 创建装配体任务
        assembly_name = params.get("name", "assembly")
        assembly_task = self._create_task(
            tool="create_assembly",
            description=f"Create assembly: {assembly_name}" +
                         (f" (subassembly)" if is_subassembly else ""),
            parameters={
                "name": assembly_name,
                "is_subassembly": is_subassembly,
                "component_count": component_count
            },
            dependencies=dependencies.copy() if dependencies else []
        )
        tasks.append(assembly_task)

        return tasks

    def _decompose_modify_assembly(self, intent: Intent) -> List[Task]:
        """
        分解修改装配体的意图（ENH-01）

        支持的操作：
        - 添加配合（mate_type参数）
        - 创建爆炸视图（view_type=exploded）
        - 修改材料（material参数）
        """
        params = intent.parameters or {}
        tasks = []

        # 检查是否有配合类型参数
        if "mate_type" in params:
            mate_type = params["mate_type"]
            return self._decompose_add_mate(mate_type)

        # 检查是否有视图类型参数
        if "view_type" in params:
            view_type = params["view_type"]
            if view_type == "exploded":
                return self._decompose_exploded_view()

        # 检查是否有材料参数
        if "material" in params:
            material = params["material"]
            return [self._create_task(
                tool="assign_material",
                description=f"Assign material {material} to assembly",
                parameters={"material": material}
            )]

        # 如果没有明确的修改类型，返回通用修改任务
        return [self._create_task(
            tool="modify_assembly",
            description="Modify assembly",
            parameters=params
        )]

    def _decompose_add_mate(self, mate_type: str) -> List[Task]:
        """
        分解添加配合的操作（ENH-01）

        支持的配合类型：
        - coaxial: 同轴配合
        - coincident: 重合配合
        - parallel: 平行配合
        - perpendicular: 垂直配合
        - distance: 距离配合
        - angle: 角度配合
        """
        # 配合类型映射到描述
        mate_descriptions = {
            "coaxial": "coaxial mate",
            "coincident": "coincident mate",
            "parallel": "parallel mate",
            "perpendicular": "perpendicular mate",
            "distance": "distance mate",
            "angle": "angle mate"
        }

        description = mate_descriptions.get(mate_type, f"{mate_type} mate")

        return [self._create_task(
            tool="add_mate",
            description=f"Add {description}",
            parameters={"mate_type": mate_type}
        )]

    def _decompose_analyze_assembly(self, intent: Intent) -> List[Task]:
        """
        分解分析装配体的意图（ENH-01）

        支持的分析类型：
        - interference: 干涉检查
        - clearance: 间隙检查
        """
        params = intent.parameters or {}
        check_type = params.get("check_type", "interference")

        if check_type == "interference":
            return [self._create_task(
                tool="check_interference",
                description="Check for interference between components",
                parameters={"check_type": "interference"}
            )]
        elif check_type == "clearance":
            return [self._create_task(
                tool="check_clearance",
                description="Check clearance between components",
                parameters={"check_type": "clearance"}
            )]
        else:
            raise ValueError(f"Unknown check type: {check_type}")

    def _decompose_exploded_view(self) -> List[Task]:
        """
        分解创建爆炸视图的操作（ENH-01）

        爆炸视图是装配体的特殊视图，显示所有组件沿指定方向分离
        """
        return [self._create_task(
            tool="create_exploded_view",
            description="Create exploded view of assembly",
            parameters={"view_type": "exploded"}
        )]

    def _decompose_modify_drawing(self, intent: Intent) -> List[Task]:
        """
        分解修改工程图的意图（ENH-02）

        支持的操作：
        - 添加尺寸标注（annotation=dimensions）
        - 添加注释（annotation=note）
        - 修改图纸格式（sheet_format参数）
        - 修改比例（scale参数）
        """
        params = intent.parameters or {}
        tasks = []

        # 检查是否有标注类型参数
        if "annotation" in params:
            annotation_type = params["annotation"]

            if annotation_type == "dimensions":
                return [self._create_task(
                    tool="add_dimensions",
                    description="Add all dimensions to drawing",
                    parameters={"scope": "all"}
                )]
            elif annotation_type == "note":
                return [self._create_task(
                    tool="add_annotation",
                    description="Add technical note to drawing",
                    parameters={
                        "content": params.get("content", "技术要求"),
                        "position": params.get("position", "bottom")
                    }
                )]

        # 如果没有明确的修改类型，返回通用修改任务
        return [self._create_task(
            tool="modify_drawing",
            description="Modify drawing",
            parameters=params
        )]
