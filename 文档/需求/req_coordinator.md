# Coordinator Integration Requirements

## Module: Coordinator (C)
**Purpose**: Main orchestrator that integrates all 6 modules into end-to-end design automation flow

---

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| C-01 | 完整流程 - 创建立方体 | user_input="创建一个10x10x10的立方体", use_claude=False, use_real_sw=False | CoordinatorResult(success=True, tasks_executed=1, tasks_passed=1, total_time>0, feedback包含"成功创建") | 端到端流程验证 |
| C-02 | 完整流程 - 多任务设计 | user_input="创建立方体然后倒角", use_claude=False, use_real_sw=False | CoordinatorResult(success=True, tasks_executed=2, tasks_passed=2, feedback包含任务列表) | 多任务串行执行 |
| C-03 | 意图理解失败 | user_input="", use_claude=False | CoordinatorResult(success=False, error_type="IntentError", feedback包含"无法理解") | 空输入处理 |
| C-04 | 任务分解失败 | user_input="创建一个不存在的特征", use_claude=False | CoordinatorResult(success=False, error_type="DecompositionError", feedback包含"无法分解") | 无效特征处理 |
| C-05 | 任务执行失败 | user_input="创建尺寸为0的立方体", use_claude=False | CoordinatorResult(success=False, error_type="ExecutionError", feedback包含"执行失败") | 执行错误处理 |
| C-06 | 验证失败反馈 | user_input="创建立方体" (mock验证失败), use_claude=False, use_real_sw=False | CoordinatorResult(success=False, error_type="ValidationError", feedback包含"验证未通过") | 验证失败场景 |
| C-07 | Claude模式 - 简单设计 | user_input="Create a 10mm cube", use_claude=True, use_real_sw=False | CoordinatorResult(success=True, intent="create_cube", feedback包含英文理解) | Claude API模式 |
| C-08 | 本地模式 - 中文设计 | user_input="创建一个圆角矩形", use_claude=False, use_real_sw=False | CoordinatorResult(success=True, intent="create_fillet", feedback包含中文理解) | 本地意图引擎 |
| C-09 | 真实SW模式 | user_input="创建立方体", use_claude=False, use_real_sw=True | CoordinatorResult(success=True, mode="real_solidworks", feedback包含"SolidWorks") | 真实SW调用(需SW环境) |
| C-10 | Mock模式 - 离线测试 | user_input="创建立方体", use_claude=False, use_real_sw=False | CoordinatorResult(success=True, mode="mock", feedback包含"模拟") | 离线模拟模式 |
| C-11 | 执行时间跟踪 | user_input="创建立方体", use_claude=False, use_real_sw=False | CoordinatorResult(total_time>0, breakdown包含intent_time, decomposition_time等) | 各阶段耗时统计 |
| C-12 | 部分成功场景 | user_input="创建立方体然后倒角" (第二个任务失败), use_claude=False | CoordinatorResult(success=False, tasks_executed=2, tasks_passed=1, feedback包含部分成功信息) | 部分任务失败 |
| C-13 | 无任务生成 | user_input="你好", use_claude=False | CoordinatorResult(success=False, error_type="NoTasksError", feedback包含"无法生成任务") | 无效输入处理 |
| C-14 | 知识库查询集成 | user_input="如何创建拉伸特征", use_claude=False | CoordinatorResult(success=True, feedback包含"拉伸"相关知识) | 知识库辅助 |
| C-15 | 异常恢复 - 网络错误 | user_input="创建立方体", use_claude=True (模拟网络错误) | CoordinatorResult(success=False, error_type="ClaudeAPIError", feedback包含"网络或API错误") | Claude API异常 |

---

## Requirements Summary

**Core Functionality:**
- Orchestrate all 6 modules: Knowledge, Intent, Decomposer, Tool, Executor, Validator
- Process design request end-to-end: intent → tasks → execution → validation
- Generate user-friendly feedback with rich context

**Error Handling:**
- Gracefully handle failures at each stage (intent, decomposition, execution, validation)
- Provide clear error messages for each failure type
- Support partial success scenarios

**Modes:**
- Mock mode (offline testing)
- Real SolidWorks mode (requires SW environment)
- Claude API mode (uses Claude for intent)
- Local intent mode (uses regex/pattern matching)

**Performance:**
- Track total execution time
- Break down time per stage
- Return detailed CoordinatorResult

**Integration Points:**
- KnowledgeBase: Query relevant design knowledge
- IntentEngine: Understand user input (Claude/local)
- TaskDecomposer: Break down into tool tasks
- ToolRegistry: Resolve and execute tools
- TaskExecutor: Execute with parameters
- ResultValidator: Validate execution results
