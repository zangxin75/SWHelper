# SolidWorks AI Agent - 第一阶段设计文档

**项目**: Claude Code + SolidWorks 2026 API 自动化设计Agent
**阶段**: 第一阶段 - 基础Agent框架
**设计日期**: 2026-04-13
**设计者**: Claude Code AI Assistant
**状态**: ✅ 已批准

---

## 文档概述

本文档详细描述了SolidWorks AI Agent第一阶段"基础Agent框架"的完整设计，包括架构设计、模块划分、数据结构、接口定义、测试策略和实施计划。

**设计原则**:
- 遵循RDD(需求驱动开发)规范
- 自底向上建立稳固基础
- Mock开发(80%) + 真实验证(20%)的混合策略
- 完整Claude API集成支持

---

## 目录

1. [整体架构设计](#1-整体架构设计)
2. [模块详细设计](#2-模块详细设计)
3. [数据结构和接口](#3-数据结构和接口)
4. [错误处理设计](#4-错误处理设计)
5. [测试策略](#5-测试策略)
6. [实施计划](#6-实施计划)

---

## 1. 整体架构设计

### 1.1 系统分层架构

```
┌─────────────────────────────────────────────────┐
│          用户交互层 (CLI / API / GUI)            │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│       AgentCoordinator (协调层)                  │
│  process_design_request() - 主入口               │
│  流程编排 + 异常处理 + 结果反馈                  │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼────────┐ ┌▼──────────────┐
│ 意图理解      │ │任务分解   │ │工具调用封装    │
│_understand_   │ │_decompose │ │_execute_task  │
│intent()       │ │_tasks()   │ │()             │
└───────┬──────┘ └──┬────────┘ └┬──────────────┘
        │           │            │
        └───────────┼────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│          底层服务层                              │
│  知识库 | MCP工具 | Claude API | 验证器       │
└─────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

1. **单一职责**: 每个模块只做一件事
2. **依赖注入**: 所有外部依赖通过构造函数注入
3. **错误隔离**: 每层独立错误处理
4. **可观测性**: 关键操作日志记录

### 1.3 数据流设计

```
用户输入(自然语言)
    ↓
意图理解 → 结构化意图 {"action": "create", "object": "part", ...}
    ↓
任务分解 → 任务列表 [{"tool": "create_part", ...}, ...]
    ↓
工具调用 → 执行结果 {"success": true, "result": ...}
    ↓
结果验证 → 验证报告 {"passed": true, "issues": []}
    ↓
用户反馈 → 友好消息 "✅ 设计任务完成!"
```

---

## 2. 模块详细设计

### 2.1 模块1: 知识库管理

**文件**: `代码/Python脚本/knowledge_base.py`

**职责**:
- 管理设计知识库(材料属性、设计规则、标准件库)
- 提供查询接口

**核心方法**:
```python
class KnowledgeBase:
    def get_material(self, name: str) -> dict
    def get_design_rule(self, rule_name: str) -> any
    def search_standard_component(self, type_: str, size: str) -> dict
```

**依赖**: 无(纯数据查询)
**测试类型**: 单元测试
**测试覆盖率**: ≥ 95%

---

### 2.2 模块2: 意图理解

**文件**: `代码/Python脚本/intent_understanding.py`

**职责**:
- 解析用户的自然语言输入
- 识别动作、对象、参数
- 支持Claude API增强和本地规则两种模式

**核心方法**:
```python
class IntentUnderstanding:
    async def understand(self, user_input: str, use_claude: bool = True) -> Intent
```

**返回结构**:
```python
{
    "action": "create",  # create/modify/analyze/export
    "object": "part",    # part/assembly/drawing
    "parameters": {
        "dimensions": [100, 100, 50],
        "material": "铝合金_6061"
    },
    "constraints": ["拔模角度1-3度"],
    "confidence": 0.95
}
```

**依赖**: Claude API(可选), 正则表达式(本地模式)
**测试类型**: 集成测试(Mock Claude API)
**测试覆盖率**: ≥ 90%

---

### 2.3 模块3: 任务分解

**文件**: `代码/Python脚本/task_decomposition.py`

**职责**:
- 将结构化意图分解为可执行的任务序列
- 考虑任务之间的依赖关系
- 优化任务顺序

**核心方法**:
```python
class TaskDecomposer:
    async def decompose(self, intent: Intent) -> List[Task]
```

**返回任务示例**:
```python
[
    {
        "id": "t1",
        "tool": "create_part",
        "description": "创建新零件文档",
        "parameters": {"template": "part"},
        "dependencies": []
    },
    {
        "id": "t2",
        "tool": "create_sketch",
        "description": "创建100x100矩形草图",
        "dependencies": ["t1"]
    }
]
```

**依赖**: 意图理解模块
**测试类型**: 单元测试
**测试覆盖率**: ≥ 90%

---

### 2.4 模块4: 工具调用封装

**文件**: `代码/Python脚本/tool_wrapper.py`

**职责**:
- 封装106个MCP工具为统一接口
- 处理参数转换和错误重试
- 支持mock模式

**核心方法**:
```python
class ToolWrapper:
    def __init__(self, use_mock: bool = False)
    async def call_tool(self, tool_name: str, parameters: dict) -> ToolResult
    def list_available_tools(self) -> List[str]
```

**依赖**: MCP适配器
**测试类型**: 集成测试(Mock MCP)
**测试覆盖率**: ≥ 85%

---

### 2.5 模块5: 任务执行编排

**文件**: `代码/Python脚本/task_executor.py`

**职责**:
- 按依赖关系执行任务序列
- 并行执行无依赖的任务
- 跟踪执行状态

**核心方法**:
```python
class TaskExecutor:
    async def execute(self, tasks: List[Task]) -> ExecutionResult
    async def _execute_with_dependencies(self, task: Task, completed: set) -> result
```

**依赖**: 工具调用封装
**测试类型**: 单元测试
**测试覆盖率**: ≥ 90%

---

### 2.6 模块6: 结果验证

**文件**: `代码/Python脚本/result_validator.py`

**职责**:
- 验证设计结果的正确性
- 检查设计规则合规性
- 生成验证报告

**核心方法**:
```python
class ResultValidator:
    async def validate(self, results: List[ToolResult], intent: Intent) -> ValidationReport
    def check_design_rules(self, result: ToolResult) -> List[str]
```

**验证报告结构**:
```python
{
    "passed": bool,
    "issues": ["问题描述"],
    "warnings": ["警告信息"],
    "metrics": {"质量": 1.2, "体积": 500000}
}
```

**依赖**: 知识库管理, SW API
**测试类型**: 集成测试
**测试覆盖率**: ≥ 85%

---

### 2.7 模块7: AgentCoordinator整合

**文件**: `代码/Python脚本/agent_coordinator.py`

**职责**:
- 协调所有模块,实现端到端流程
- 处理异常和用户交互
- 生成友好的用户反馈

**核心方法**:
```python
class AgentCoordinator:
    def __init__(self, use_mock: bool = False, use_claude: bool = True)
    async def process_design_request(self, user_input: str) -> CoordinatorResult
    def generate_feedback(self, result: CoordinatorResult) -> str
```

**主流程**:
```
意图理解 → 任务分解 → 执行 → 验证 → 反馈
```

**依赖**: 所有其他模块
**测试类型**: E2E测试(真实SW环境)
**测试覆盖率**: ≥ 70%

---

## 3. 数据结构和接口

### 3.1 Pydantic数据模型

**文件**: `代码/Python脚本/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class ActionType(str, Enum):
    CREATE = "create"
    MODIFY = "modify"
    ANALYZE = "analyze"
    EXPORT = "export"

class ObjectType(str, Enum):
    PART = "part"
    ASSEMBLY = "assembly"
    DRAWING = "drawing"

class Intent(BaseModel):
    """结构化意图"""
    action: ActionType
    object: ObjectType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_input: str

class Task(BaseModel):
    """可执行任务"""
    id: str
    tool: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)

class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    tool_name: str
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str

class ExecutionResult(BaseModel):
    """任务执行结果"""
    results: List[ToolResult]
    failed_tasks: List[str] = Field(default_factory=list)
    total_time: float
    success_count: int
    failure_count: int

class ValidationReport(BaseModel):
    """验证报告"""
    passed: bool
    issues: List[ValidationIssue] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)

class CoordinatorResult(BaseModel):
    """协调器最终结果"""
    success: bool
    intent: Intent
    tasks: List[Task]
    execution: ExecutionResult
    validation: ValidationReport
    user_feedback: str
    total_time: float
```

### 3.2 接口抽象

**文件**: `代码/Python脚本/interfaces.py`

```python
from abc import ABC, abstractmethod

class IKnowledgeBase(ABC):
    @abstractmethod
    def get_material(self, name: str) -> dict: pass

    @abstractmethod
    def get_design_rules(self, category: str) -> dict: pass

class IIntentUnderstanding(ABC):
    @abstractmethod
    async def understand(self, user_input: str) -> Intent: pass

class ITaskDecomposer(ABC):
    @abstractmethod
    async def decompose(self, intent: Intent) -> List[Task]: pass

class IToolWrapper(ABC):
    @abstractmethod
    async def call_tool(self, tool_name: str, parameters: dict) -> ToolResult: pass

    @abstractmethod
    def list_tools(self) -> List[str]: pass

class ITaskExecutor(ABC):
    @abstractmethod
    async def execute(self, tasks: List[Task]) -> ExecutionResult: pass

class IResultValidator(ABC):
    @abstractmethod
    async def validate(self, results: List[ToolResult], intent: Intent) -> ValidationReport: pass
```

---

## 4. 错误处理设计

### 4.1 异常层次结构

**文件**: `代码/Python脚本/exceptions.py`

```python
class AgentError(Exception):
    """Agent基础异常"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class IntentUnderstandingError(AgentError):
    """意图理解错误"""
    pass

class TaskDecompositionError(AgentError):
    """任务分解错误"""
    pass

class ToolExecutionError(AgentError):
    """工具执行错误"""
    def __init__(self, tool_name: str, message: str, details: dict = None):
        self.tool_name = tool_name
        super().__init__(message, details)

class ValidationError(AgentError):
    """验证错误"""
    pass

class ConfigurationError(AgentError):
    """配置错误"""
    pass
```

### 4.2 错误处理装饰器

```python
def handle_agent_errors(func):
    """统一错误处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AgentError:
            raise
        except Exception as e:
            raise AgentError(f"Unexpected error in {func.__name__}: {str(e)}")
    return wrapper
```

---

## 5. 测试策略

### 5.1 测试金字塔

```
        ┌─────────────┐
        │  E2E测试    │  5%  - 真实SW环境
        ├─────────────┤
        │  集成测试   │  15% - Mock外部依赖
        ├─────────────┤
        │  单元测试   │  80% - 纯逻辑测试
        └─────────────┘
```

### 5.2 测试分层

#### 单元测试 (80%)
- 运行速度: 毫秒级
- 无外部依赖
- 示例: 知识库查询、数据验证

#### 集成测试 (15%)
- 运行速度: 秒级
- Mock外部依赖
- 示例: 意图理解+任务分解集成

#### E2E测试 (5%)
- 运行速度: 分钟级
- 真实SW环境
- 示例: 完整对话创建零件

### 5.3 测试覆盖率目标

| 模块 | 单元测试 | 集成测试 | E2E测试 | 总覆盖率 |
|------|---------|---------|---------|---------|
| 知识库管理 | 95% | ✓ | - | ≥ 95% |
| 意图理解 | 90% | ✓ | ✓ | ≥ 90% |
| 任务分解 | 90% | ✓ | - | ≥ 90% |
| 工具调用 | 85% | ✓ | ✓ | ≥ 85% |
| 任务执行 | 90% | ✓ | - | ≥ 90% |
| 结果验证 | 85% | ✓ | ✓ | ≥ 85% |
| Coordinator | 70% | - | ✓ | ≥ 70% |

**总体目标**: 代码覆盖率 ≥ 85%

### 5.4 测试运行策略

**本地开发**: 每次修改后运行快速测试
```bash
pytest 代码/测试代码/ -m "not e2e" -x
```

**提交前**: 运行所有非E2E测试
```bash
pytest 代码/测试代码/ -m "not e2e" --cov
```

**CI/CD**:
- 每次PR: 单元+集成测试
- 每天晚上: 完整测试(包括E2E)
- 发布前: 必须通过所有测试

---

## 6. 实施计划

### 6.1 开发时间线

```
第1周: 基础设施层
├── [1天] 项目结构 + Pydantic模型 + 接口定义
├── [2天] 模块1: 知识库管理
└── [2天] 模块4: 工具调用封装

第2周: 核心逻辑层
├── [2天] 模块2: 意图理解
├── [2天] 模块3: 任务分解
└── [1天] 模块5: 任务执行编排

第3周: 验证和整合层
├── [2天] 模块6: 结果验证
├── [2天] 模块7: Coordinator整合
└── [1天] 集成测试和问题修复

总计: 15个工作日 (3周)
```

### 6.2 里程碑

| 里程碑 | 时间 | 验证标准 | 展示内容 |
|--------|------|---------|---------|
| M1: 基础层完成 | 第1周结束 | 知识库+工具调用测试全绿 | 查询材料信息 |
| M2: 核心逻辑完成 | 第2周结束 | 意图+分解测试全绿 | 解析用户需求 |
| M3: 完整流程 | 第3周结束 | 所有测试全绿 | 对话创建方块 |

### 6.3 并行开发机会

- **并行组1**: 知识库 + 工具调用(无依赖)
- **并行组2**: 意图理解 + 任务分解(串行)
- **串行**: 验证 + Coordinator(需要所有模块)

### 6.4 风险和缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| SW API不稳定 | 高 | 中 | Mock开发 |
| Claude API成本 | 中 | 低 | 本地模式降级 |
| 需求理解偏差 | 高 | 中 | 确认需求表 |
| 测试环境问题 | 中 | 中 | 容器化环境 |
| 时间超期 | 中 | 低 | 模块独立 |

---

## 7. 交付物清单

### 7.1 文档
- ✅ 7个需求表 (`文档/需求/req_*.md`)
- ✅ 本设计文档

### 7.2 代码
- ✅ 7个业务模块 (`代码/Python脚本/*.py`)
- ✅ Pydantic数据模型 (`schemas.py`)
- ✅ 接口定义 (`interfaces.py`)
- ✅ 异常处理 (`exceptions.py`)

### 7.3 测试
- ✅ 7个测试文件 (`代码/测试代码/test_*.py`)
- ✅ 测试覆盖率 ≥ 85%

### 7.4 演示
- ✅ 端到端演示: 对话创建简单方块零件
- ✅ CLI交互界面

---

## 8. 附录

### 8.1 关键技术栈
- Python 3.10+
- Pydantic (数据验证)
- pytest + pytest-asyncio (测试)
- Anthropic API (Claude集成)
- SolidWorks MCP Server (106工具)

### 8.2 参考资料
- RDD开发规范: `文档/项目管理/需求驱动开发模板_RDD.md`
- 实施方案: `文档/技术文档/Claude_Code_+_SolidWorks_2026_API_自动化设计Agent_实施方案_技术文档.md`
- SolidWorks MCP文档: `文档/技术文档/SolidWorks_MCP_Server_技术文档.md`

---

**文档版本**: 1.0
**最后更新**: 2026-04-13
**状态**: ✅ 设计已批准,待实施

---

<div align="center">

### 🎯 第一阶段设计完成!准备进入实施阶段。

</div>
