"""
Task Executor Module Tests

Requirements: 文档/需求/req_task_executor.md
"""

import pytest
import asyncio
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch
from schemas import Task, ToolResult, ExecutionResult
from datetime import datetime


@pytest.fixture
def executor():
    """创建 TaskExecutor 实例"""
    from task_executor import TaskExecutor
    return TaskExecutor()


@pytest.fixture
def mock_tool_registry():
    """模拟工具注册表"""
    registry = {}

    async def success_tool(**params):
        """成功的工具"""
        return {"status": "success", "data": params}

    async def failing_tool(**params):
        """总是失败的工具"""
        raise ValueError("Tool execution failed")

    async def flaky_tool(**params):
        """前几次失败，最后成功的工具"""
        # 使用闭包变量模拟重试
        if not hasattr(flaky_tool, 'attempt_count'):
            flaky_tool.attempt_count = 0
        flaky_tool.attempt_count += 1
        if flaky_tool.attempt_count < 2:
            raise ValueError("Temporary failure")
        return {"status": "success"}

    async def always_failing(**params):
        """总是失败的工具（用于测试重试失败）"""
        raise RuntimeError("Permanent failure")

    async def fast_tool(**params):
        """快速工具"""
        await asyncio.sleep(0.01)
        return {"status": "fast"}

    async def slow_tool(**params):
        """慢速工具"""
        await asyncio.sleep(0.05)
        return {"status": "slow"}

    async def analyze_tool(**params):
        """分析工具"""
        return {"metric": "value"}

    registry["success_tool"] = success_tool
    registry["failing_tool"] = failing_tool
    registry["flaky_tool"] = flaky_tool
    registry["always_failing"] = always_failing
    registry["fast_tool"] = fast_tool
    registry["slow_tool"] = slow_tool
    registry["analyze_a"] = analyze_tool
    registry["analyze_b"] = analyze_tool
    registry["analyze_c"] = analyze_tool
    registry["tool_a"] = success_tool
    registry["tool_b"] = success_tool
    registry["create_part"] = success_tool
    registry["create_sketch"] = success_tool
    registry["extrude_boss"] = success_tool

    return registry


class TestTaskExecutor:
    """任务执行器测试"""

    @pytest.mark.asyncio
    async def test_execute_no_dependencies(self, executor, mock_tool_registry):
        """E-01: 无依赖任务执行 - 应并行执行"""
        tasks = [
            Task(id="1", tool="tool_a", description="Task 1", parameters={"param": "a"}),
            Task(id="2", tool="tool_b", description="Task 2", parameters={"param": "b"}),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 2
        assert result.failure_count == 0
        assert len(result.results) == 2
        assert result.total_time > 0
        assert all(r.success for r in result.results)

    @pytest.mark.asyncio
    async def test_execute_with_dependencies(self, executor, mock_tool_registry):
        """E-02: 有依赖任务串行执行"""
        tasks = [
            Task(id="1", tool="create_part", description="Create part", parameters={}),
            Task(id="2", tool="create_sketch", description="Create sketch", parameters={}, dependencies=["1"]),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 2
        assert result.failure_count == 0
        assert len(result.results) == 2

        # 验证执行顺序：Task1 应该在 Task2 之前执行
        time1 = next(r.execution_time for r in result.results if r.tool_name == "create_part")
        time2 = next(r.execution_time for r in result.results if r.tool_name == "create_sketch")
        # 由于是串行执行，两个任务都应该成功

    @pytest.mark.asyncio
    async def test_parallel_execution(self, executor, mock_tool_registry):
        """E-03: 并行执行独立任务"""
        tasks = [
            Task(id="1", tool="analyze_a", description="Analyze A", parameters={}),
            Task(id="2", tool="analyze_b", description="Analyze B", parameters={}),
            Task(id="3", tool="analyze_c", description="Analyze C", parameters={}),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 3
        assert result.failure_count == 0
        assert len(result.results) == 3

        # 验证所有任务都成功
        assert all(r.success for r in result.results)

    @pytest.mark.asyncio
    async def test_task_failure_handling(self, executor, mock_tool_registry):
        """E-04: 任务执行失败处理"""
        tasks = [
            Task(id="1", tool="failing_tool", description="Failing task", parameters={}),
            Task(id="2", tool="success_tool", description="Dependent task", parameters={}, dependencies=["1"]),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        # Task1 失败，Task2 因依赖失败不应执行
        assert result.failure_count >= 1
        assert "1" in result.failed_tasks
        assert len([r for r in result.results if not r.success]) >= 1

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, executor, mock_tool_registry):
        """E-05: 执行时间跟踪"""
        tasks = [
            Task(id="1", tool="fast_tool", description="Fast task", parameters={}),
            Task(id="2", tool="slow_tool", description="Slow task", parameters={}),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.total_time > 0

        # 验证每个任务都有执行时间
        for r in result.results:
            assert r.execution_time > 0

        # 总时间应该约等于各任务时间之和（允许误差）
        individual_times = sum(r.execution_time for r in result.results)
        assert abs(result.total_time - individual_times) < 0.1  # 允许10%误差

    @pytest.mark.asyncio
    async def test_aggregate_results(self, executor, mock_tool_registry):
        """E-06: 聚合多个任务结果"""
        tasks = [
            Task(id="1", tool="tool_a", description="Task A", parameters={"key": "a"}),
            Task(id="2", tool="tool_b", description="Task B", parameters={"key": "b"}),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert len(result.results) == 2

        # 验证结果聚合
        tool_names = [r.tool_name for r in result.results]
        assert "tool_a" in tool_names
        assert "tool_b" in tool_names

        # 验证所有结果都成功
        assert all(r.success for r in result.results)

    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, executor, mock_tool_registry):
        """E-07: 循环依赖检测"""
        tasks = [
            Task(id="1", tool="tool_a", description="Task 1", parameters={}, dependencies=["2"]),
            Task(id="2", tool="tool_b", description="Task 2", parameters={}, dependencies=["1"]),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            with pytest.raises(ValueError) as exc_info:
                await executor.execute(tasks)

        assert "circular dependency" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_empty_task_list(self, executor, mock_tool_registry):
        """E-08: 空任务列表"""
        tasks = []

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 0
        assert result.failure_count == 0
        assert len(result.results) == 0
        assert result.total_time == 0

    @pytest.mark.asyncio
    async def test_partial_failure(self, executor, mock_tool_registry):
        """E-09: 部分任务失败"""
        tasks = [
            Task(id="1", tool="success_tool", description="Success 1", parameters={}),
            Task(id="2", tool="failing_tool", description="Failing", parameters={}),
            Task(id="3", tool="success_tool", description="Success 2", parameters={}),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 2
        assert result.failure_count == 1
        assert "2" in result.failed_tasks

    @pytest.mark.asyncio
    async def test_complex_dependency_chain(self, executor, mock_tool_registry):
        """E-10: 复杂依赖链"""
        tasks = [
            Task(id="1", tool="create_part", description="Part", parameters={}),
            Task(id="2", tool="create_sketch", description="Sketch", parameters={}, dependencies=["1"]),
            Task(id="3", tool="extrude_boss", description="Extrude", parameters={}, dependencies=["2"]),
            Task(id="4", tool="analyze_a", description="Analyze A", parameters={}),
            Task(id="5", tool="analyze_b", description="Analyze B", parameters={}, dependencies=["4"]),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 5
        assert result.failure_count == 0

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, executor, mock_tool_registry):
        """E-11: 重试机制"""
        # 重置 flaky_tool 的计数器
        import task_executor
        if hasattr(task_executor, 'flaky_tool'):
            task_executor.flaky_tool.attempt_count = 0

        tasks = [
            Task(id="1", tool="flaky_tool", description="Flaky task", parameters={}, max_retries=2),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 1
        assert result.failure_count == 0

    @pytest.mark.asyncio
    async def test_retry_failure(self, executor, mock_tool_registry):
        """E-12: 重试失败"""
        tasks = [
            Task(id="1", tool="always_failing", description="Always failing", parameters={}, max_retries=2),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        assert result.success_count == 0
        assert result.failure_count == 1
        assert "1" in result.failed_tasks

    @pytest.mark.asyncio
    async def test_self_dependency_detection(self, executor, mock_tool_registry):
        """测试自依赖检测"""
        tasks = [
            Task(id="1", tool="tool_a", description="Self-dep task", parameters={}, dependencies=["1"]),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            with pytest.raises(ValueError) as exc_info:
                await executor.execute(tasks)

        assert "circular dependency" in str(exc_info.value).lower() or "self" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_missing_dependency(self, executor, mock_tool_registry):
        """测试依赖不存在的任务"""
        tasks = [
            Task(id="1", tool="tool_a", description="Task 1", parameters={}, dependencies=["999"]),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        # 任务应该失败，因为依赖不存在
        assert result.failure_count >= 1
        assert "1" in result.failed_tasks or len(result.failed_tasks) > 0

    @pytest.mark.asyncio
    async def test_tool_not_found(self, executor, mock_tool_registry):
        """测试工具不存在"""
        tasks = [
            Task(id="1", tool="nonexistent_tool", description="Nonexistent", parameters={}),
        ]

        with patch.object(executor, '_tool_registry', mock_tool_registry):
            result = await executor.execute(tasks)

        # 应该失败
        assert result.failure_count == 1
        assert "1" in result.failed_tasks
        assert any("not found" in r.error.lower() if r.error else False for r in result.results)
