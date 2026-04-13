"""
Task Decomposition Module Tests

Requirements: 文档/需求/req_task_decomposition.md
"""

import pytest
from typing import List
from schemas import Intent, Task, ActionType, ObjectType


@pytest.fixture
def decomposer():
    """创建 TaskDecomposer 实例"""
    from task_decomposition import TaskDecomposer
    return TaskDecomposer()


class TestTaskDecomposition:
    """任务分解测试"""

    @pytest.mark.parametrize("intent,expected_tools,expected_params,deps", [
        # D-01: CREATE 意图分解 - 创建立方体
        (
            Intent(
                action=ActionType.CREATE,
                object=ObjectType.PART,
                parameters={"name": "test", "type": "cube", "width": 10, "height": 20, "depth": 30},
                raw_input="create cube test"
            ),
            ["create_part", "create_sketch", "create_rectangle", "extrude_boss"],
            [
                {"name": "test"},
                {"plane": "Front"},
                {"width": 10, "height": 20},
                {"depth": 30, "direction": "blind"}
            ],
            [[], [0], [1], [2]]  # dependencies
        ),
        # D-02: CREATE 意图分解 - 创建圆柱
        (
            Intent(
                action=ActionType.CREATE,
                object=ObjectType.PART,
                parameters={"name": "cylinder", "type": "cylinder", "diameter": 15, "height": 40},
                raw_input="create cylinder"
            ),
            ["create_part", "create_sketch", "create_circle", "extrude_boss"],
            [
                {"name": "cylinder"},
                {"plane": "Front"},
                {"diameter": 15},
                {"depth": 40, "direction": "blind"}
            ],
            [[], [0], [1], [2]]
        ),
    ], ids=["D-01_CREATE_cube", "D-02_CREATE_cylinder"])
    def test_decompose_create_intent(self, decomposer, intent, expected_tools, expected_params, deps):
        """测试 CREATE 意图分解"""
        tasks = decomposer.decompose(intent)

        # 验证任务数量
        assert len(tasks) == len(expected_tools)

        # 验证每个任务的工具和参数
        for i, task in enumerate(tasks):
            assert task.tool == expected_tools[i], f"Task {i}: tool mismatch"
            assert task.parameters == expected_params[i], f"Task {i}: params mismatch"

        # 验证依赖关系
        for i, expected_dep_indices in enumerate(deps):
            actual_task = tasks[i]
            # 验证依赖数量
            assert len(actual_task.dependencies) == len(expected_dep_indices), f"Task {i}: wrong number of dependencies"
            # 验证每个依赖是否指向正确的任务
            for dep_index in expected_dep_indices:
                expected_dep_id = tasks[dep_index].id
                assert expected_dep_id in actual_task.dependencies, f"Task {i} should depend on task {dep_index}"

    @pytest.mark.parametrize("intent,expected_tools,expected_params", [
        # D-03: MODIFY 意图分解 - 修改尺寸
        (
            Intent(
                action=ActionType.MODIFY,
                object=ObjectType.PART,
                parameters={"feature": "Sketch1", "dimension": "D1", "value": 50.0},
                raw_input="modify dimension"
            ),
            ["modify_dimension"],
            [{"feature": "Sketch1", "dimension": "D1", "value": 50.0}]
        ),
        # D-04: MODIFY 意图分解 - 修改特征参数
        (
            Intent(
                action=ActionType.MODIFY,
                object=ObjectType.PART,
                parameters={"name": "Extrude1", "depth": 25.0},
                raw_input="modify feature"
            ),
            ["modify_feature"],
            [{"name": "Extrude1", "depth": 25.0}]
        ),
    ], ids=["D-03_MODIFY_dimension", "D-04_MODIFY_feature"])
    def test_decompose_modify_intent(self, decomposer, intent, expected_tools, expected_params):
        """测试 MODIFY 意图分解"""
        tasks = decomposer.decompose(intent)

        assert len(tasks) == len(expected_tools)
        for i, task in enumerate(tasks):
            assert task.tool == expected_tools[i]
            assert task.parameters == expected_params[i]
            assert len(task.dependencies) == 0  # MODIFY tasks have no dependencies

    @pytest.mark.parametrize("intent,expected_tools,expected_params", [
        # D-05: ANALYZE 意图分解 - 测量体积
        (
            Intent(
                action=ActionType.ANALYZE,
                object=ObjectType.PART,
                parameters={"metric": "volume"},
                raw_input="analyze volume"
            ),
            ["get_mass_properties"],
            [{}]
        ),
        # D-06: ANALYZE 意图分解 - 测量距离
        (
            Intent(
                action=ActionType.ANALYZE,
                object=ObjectType.PART,
                parameters={"metric": "distance", "entity1": "Point1@Sketch1", "entity2": "Point2@Sketch1"},
                raw_input="measure distance"
            ),
            ["measure_distance"],
            [{"entity1": "Point1@Sketch1", "entity2": "Point2@Sketch1"}]
        ),
    ], ids=["D-05_ANALYZE_volume", "D-06_ANALYZE_distance"])
    def test_decompose_analyze_intent(self, decomposer, intent, expected_tools, expected_params):
        """测试 ANALYZE 意图分解"""
        tasks = decomposer.decompose(intent)

        assert len(tasks) == len(expected_tools)
        for i, task in enumerate(tasks):
            assert task.tool == expected_tools[i]
            assert task.parameters == expected_params[i]

    @pytest.mark.parametrize("intent,expected_tools,expected_params", [
        # D-07: EXPORT 意图分解 - 导出 STEP
        (
            Intent(
                action=ActionType.EXPORT,
                object=ObjectType.PART,
                parameters={"format": "step", "filepath": "C:/temp/test.step"},
                raw_input="export step"
            ),
            ["export_file"],
            [{"format": "step", "filepath": "C:/temp/test.step"}]
        ),
        # D-08: EXPORT 意图分解 - 导出 PDF 图纸
        (
            Intent(
                action=ActionType.EXPORT,
                object=ObjectType.DRAWING,
                parameters={"format": "pdf", "filepath": "C:/temp/drawing.pdf"},
                raw_input="export pdf"
            ),
            ["export_drawing"],
            [{"format": "pdf", "filepath": "C:/temp/drawing.pdf"}]
        ),
    ], ids=["D-07_EXPORT_step", "D-08_EXPORT_pdf"])
    def test_decompose_export_intent(self, decomposer, intent, expected_tools, expected_params):
        """测试 EXPORT 意图分解"""
        tasks = decomposer.decompose(intent)

        assert len(tasks) == len(expected_tools)
        for i, task in enumerate(tasks):
            assert task.tool == expected_tools[i]
            assert task.parameters == expected_params[i]

    @pytest.mark.parametrize("intent,error_msg", [
        # D-09: 边界场景 - 缺少必需参数
        (
            Intent(
                action=ActionType.CREATE,
                object=ObjectType.PART,
                parameters={"name": "test", "type": "cube"},
                raw_input="create cube"
            ),
            "Missing required parameter"
        ),
        # D-12: 边界场景 - 零尺寸
        (
            Intent(
                action=ActionType.CREATE,
                object=ObjectType.PART,
                parameters={"name": "zero", "type": "cube", "width": 0, "height": 10, "depth": 10},
                raw_input="create zero cube"
            ),
            "Dimension must be positive"
        ),
    ], ids=["D-09_missing_params", "D-12_zero_dimension"])
    def test_decompose_error_cases(self, decomposer, intent, error_msg):
        """测试错误场景"""
        with pytest.raises(ValueError) as exc_info:
            decomposer.decompose(intent)
        assert error_msg in str(exc_info.value)

    @pytest.mark.parametrize("intent,expected_order", [
        # D-13: 任务依赖顺序 - 立方体
        (
            Intent(
                action=ActionType.CREATE,
                object=ObjectType.PART,
                parameters={"name": "test", "type": "cube", "width": 10, "height": 20, "depth": 30},
                raw_input="create cube test"
            ),
            ["create_part", "create_sketch", "create_rectangle", "extrude_boss"]
        ),
        # D-14: 任务依赖顺序 - 圆柱
        (
            Intent(
                action=ActionType.CREATE,
                object=ObjectType.PART,
                parameters={"name": "cylinder", "type": "cylinder", "diameter": 15, "height": 40},
                raw_input="create cylinder"
            ),
            ["create_part", "create_sketch", "create_circle", "extrude_boss"]
        ),
    ], ids=["D-13_order_cube", "D-14_order_cylinder"])
    def test_task_ordering(self, decomposer, intent, expected_order):
        """测试任务执行顺序"""
        tasks = decomposer.decompose(intent)

        # 验证任务按正确顺序排列
        actual_order = [task.tool for task in tasks]
        assert actual_order == expected_order

        # 验证依赖关系
        for i, task in enumerate(tasks):
            for dep_id in task.dependencies:
                # Find the index of the dependency task
                dep_index = -1
                for j, other_task in enumerate(tasks):
                    if other_task.id == dep_id:
                        dep_index = j
                        break
                assert dep_index >= 0, f"Task {i} depends on unknown task {dep_id}"
                assert dep_index < i, f"Task {i} depends on task {dep_index} which comes after it"

    def test_parallel_tasks(self, decomposer):
        """D-15: 并行任务 - 多个测量任务"""
        intent = Intent(
            action=ActionType.ANALYZE,
            object=ObjectType.PART,
            parameters={"metrics": ["volume", "area", "mass"]},
            raw_input="analyze metrics"
        )

        tasks = decomposer.decompose(intent)

        # 应该生成3个任务
        assert len(tasks) == 3

        # 所有任务都应该没有依赖（可并行执行）
        for task in tasks:
            assert len(task.dependencies) == 0, f"Task {task.tool} should have no dependencies for parallel execution"

    def test_empty_params(self, decomposer):
        """测试空参数"""
        intent = Intent(
            action=ActionType.MODIFY,
            object=ObjectType.PART,
            parameters={},
            raw_input="modify nothing"
        )

        with pytest.raises(ValueError, match="Missing required parameter"):
            decomposer.decompose(intent)

    def test_negative_dimension(self, decomposer):
        """测试负数尺寸"""
        intent = Intent(
            action=ActionType.CREATE,
            object=ObjectType.PART,
            parameters={"name": "negative", "type": "cube", "width": -10, "height": 20, "depth": 30},
            raw_input="create negative cube"
        )

        with pytest.raises(ValueError, match="Dimension must be positive"):
            decomposer.decompose(intent)

    def test_unknown_entity_type(self, decomposer):
        """Test: D-10 - Unknown entity type should raise error"""
        from pydantic import ValidationError as PydanticValidationError

        intent = Intent(
            action=ActionType.CREATE,
            object=ObjectType.DRAWING,  # DRAWING not supported for CREATE
            parameters={},
            confidence=0.9,
            raw_input="创建工程图"
        )

        with pytest.raises(ValueError, match="Unknown entity type"):
            decomposer.decompose(intent)

    def test_unknown_action_type(self, decomposer):
        """Test: D-11 - Unknown action type should raise error"""
        from schemas import Intent, ObjectType

        # Pydantic converts invalid enum values to UNKNOWN
        # The decompose() method should handle UNKNOWN action
        intent = Intent(
            action="unknown",  # Will be converted to ActionType.UNKNOWN
            object=ObjectType.PART,
            parameters={},
            confidence=0.5,
            raw_input="未知操作"
        )

        # Should raise ValueError in decompose()
        with pytest.raises(ValueError, match="Unknown action type"):
            decomposer.decompose(intent)
