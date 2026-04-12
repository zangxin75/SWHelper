# Task Executor Module Requirements

## Module Overview
执行任务序列，处理任务依赖关系，支持并行执行和错误恢复。

## Requirements Table

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| E-01 | 无依赖任务执行 | Task列表: [Task(id="1", tool="tool_a", params={}), Task(id="2", tool="tool_b", params={})] | ExecutionResult(success_count=2, failure_count=0, total_time>0) | 两个任务无依赖，可并行执行 |
| E-02 | 有依赖任务串行执行 | Task列表: [Task(id="1", tool="create_part"), Task(id="2", tool="create_sketch", dependencies=["1"])] | ExecutionResult(success_count=2, failure_count=0) | Task2依赖Task1，必须串行 |
| E-03 | 并行执行独立任务 | Task列表: [Task(id="1", tool="analyze_a"), Task(id="2", tool="analyze_b"), Task(id="3", tool="analyze_c")] | ExecutionResult(success_count=3, failure_count=0) | 三个任务无依赖，应并行 |
| E-04 | 任务执行失败处理 | Task列表: [Task(id="1", tool="failing_tool"), Task(id="2", tool="success_tool", dependencies=["1"])] | ExecutionResult(success_count=0或1, failure_count=1或2, failed_tasks包含失败任务ID) | Task1失败，Task2因依赖失败不应执行 |
| E-05 | 执行时间跟踪 | Task列表: [Task(id="1", tool="fast_tool"), Task(id="2", tool="slow_tool")] | ExecutionResult(total_time≈sum(individual_times), 每个ToolResult.execution_time>0) | 跟踪每个任务和总时间 |
| E-06 | 聚合多个任务结果 | Task列表: [Task(id="1", tool="tool_a"), Task(id="2", tool="tool_b")] | ExecutionResult(results=[ToolResult(success=True, tool_name="tool_a"), ToolResult(success=True, tool_name="tool_b")]) | 所有任务结果聚合在results列表 |
| E-07 | 循环依赖检测 | Task列表: [Task(id="1", dependencies=["2"]), Task(id="2", dependencies=["1"])] | 抛出 ValueError 异常，消息包含 "circular dependency" | 循环依赖应被检测并拒绝 |
| E-08 | 空任务列表 | Task列表: [] | ExecutionResult(success_count=0, failure_count=0, results=[]) | 空列表应返回空结果 |
| E-09 | 部分任务失败 | Task列表: [Task(id="1", tool="success_tool"), Task(id="2", tool="failing_tool"), Task(id="3", tool="success_tool")] | ExecutionResult(success_count=2, failure_count=1, failed_tasks=["2"]) | 独立任务，部分失败不影响其他 |
| E-10 | 复杂依赖链 | Task列表: [Task(id="1"), Task(id="2", deps=["1"]), Task(id="3", deps=["2"]), Task(id="4"), Task(id="5", deps=["4"])] | ExecutionResult(success_count=5, failure_count=0) | 两条依赖链，可并行执行 |
| E-11 | 重试机制 | Task列表: [Task(id="1", tool="flaky_tool", max_retries=2)] | ExecutionResult(success_count=1, failure_count=0) | 失败后应重试最多max_retries次 |
| E-12 | 重试失败 | Task列表: [Task(id="1", tool="always_failing", max_retries=2)] | ExecutionResult(success_count=0, failure_count=1, failed_tasks=["1"]) | 达到最大重试次数后应放弃 |

## Implementation Notes

### Dependency Resolution
- 使用拓扑排序（Kahn's algorithm）检测循环依赖
- 构建依赖图，识别可并行执行的任务层
- 每层任务使用 asyncio.gather 并行执行

### Execution Strategy
- 无依赖任务：全部并行执行
- 有依赖任务：按拓扑顺序分层执行，层内并行
- 失败任务：标记失败，其依赖任务跳过执行

### Error Handling
- 任务失败：记录 ToolResult(success=False, error=...)
- 循环依赖：抛出 ValueError，拒绝执行
- 重试：失败后在同一次执行中重试，不超过 max_retries

### Time Tracking
- 每个 ToolResult 记录 execution_time
- ExecutionResult.total_time 为所有任务时间之和
- 使用 time.perf_counter() 精确计时
