# ENH-07: 真实MCP集成 - 连接SolidWorks API

**创建日期**: 2026-04-13
**需求编号**: ENH-07-01 到 ENH-07-06
**对应实施**: Phase 2 - P0最高优先级核心功能
**优先级**: P0 (关键基础设施)

---

## 功能描述

将Agent框架从mock工具切换到真实的SolidWorks MCP Server，实现：
1. MCP客户端初始化与连接
2. 真实SolidWorks API调用
3. 端到端工作流验证
4. 错误处理与重试机制
5. 实时反馈与进度显示

---

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-07-01 | MCP客户端初始化 | 无 | MCP客户端成功连接，工具列表加载 | SolidWorks必须运行 |
| ENH-07-02 | 创建零件（真实API） | "创建一个100x100x50的方块" | SolidWorks中创建3D零件 | 调用SW真实API |
| ENH-07-03 | 创建装配体（真实API） | "创建一个装配体，2个零件" | SolidWorks中创建装配体 | 验证组件添加 |
| ENH-07-04 | 创建工程图（真实API） | "创建工程图，3个视图" | SolidWorks中创建工程图 | 验证视图生成 |
| ENH-07-05 | 错误处理（SW未运行） | 任何请求 | 返回友好错误，提示启动SW | 不崩溃 |
| ENH-07-06 | 端到端工作流 | 复杂设计请求 | 完整执行，返回实际结果 | 从意图→任务→API→结果 |

---

## 验收标准

- 6个测试用例全部通过
- 代码覆盖率 ≥80%
- 真实SolidWorks API调用成功
- 错误处理优雅
- 无回归问题

---

## 技术实现要点

### 1. MCP客户端集成

**使用MCP Python SDK**:
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 连接到SolidWorks MCP Server
server_params = StdioServerParameters(
    command="python",
    args=["-m", "solidworks_mcp"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # 初始化连接
        await session.initialize()
        # 列出可用工具
        tools = await session.list_tools()
```

### 2. 工具映射

**当前Mock工具 → 真实MCP工具**:

| Mock工具名称 | 真实MCP工具名称 | 参数映射 |
|------------|----------------|---------|
| create_part | sw_create_part | dimensions→dimensions |
| create_assembly | sw_create_assembly | component_count→component_count |
| create_drawing | sw_create_drawing | view_count, sheet_format→... |
| add_dimensions | sw_add_dimensions | (same) |
| export_drawing | sw_export_drawing | format→format |
| modify_part | sw_modify_feature | parameters→... |

### 3. 任务执行器修改

**agent_coordinator.py中的TaskExecutor**:

**当前（Mock模式）**:
```python
self.tool_registry = {
    "create_part": self._mock_create_part,
    "create_assembly": self._mock_create_assembly,
    # ... 其他mock工具
}
```

**目标（MCP模式）**:
```python
self.mcp_session = mcp_session  # MCP客户端会话
self.real_mode = True  # 标志使用真实API

async def execute_task(self, task: Task):
    if self.real_mode:
        return await self._execute_mcp_tool(task)
    else:
        return await self._execute_mock_tool(task)
```

### 4. 错误处理

**SolidWorks未运行**:
```python
try:
    result = await session.call_tool("sw_create_part", args)
except SWNotRunningError:
    return ToolResult(
        success=False,
        tool_name=task.tool,
        error="SolidWorks未运行，请先启动SolidWorks"
    )
```

**API调用失败**:
```python
except SWAPIError as e:
    # 记录错误
    # 返回友好错误信息
    # 可选：重试或降级到mock
```

### 5. 配置管理

**配置文件**: `配置/mcp_config.json`
```json
{
    "mcp_server": {
        "enabled": true,
        "command": "python",
        "args": ["-m", "solidworks_mcp"],
        "timeout": 30
    },
    "solidworks": {
        "required": true,
        "version": "2026",
        "auto_start": false
    }
}
```

---

## 实施步骤

### 步骤1: 安装MCP SDK
```bash
pip install mcp
```

### 步骤2: 创建MCP客户端包装类

**新文件**: `代码/Python脚本/mcp_client.py`
- 封装MCP连接逻辑
- 提供工具调用接口
- 处理连接状态和错误

### 步骤3: 修改TaskExecutor

**修改文件**: `代码/Python脚本/agent_coordinator.py`
- 添加MCP模式支持
- 实现工具调用路由（mock vs real）
- 添加错误处理

### 步骤4: 创建配置文件

**新文件**: `配置/mcp_config.json`
- MCP服务器配置
- SolidWorks连接配置
- 工具映射表

### 步骤5: 编写测试用例

**新文件**: `代码/测试代码/test_enh_07_real_mcp_integration.py`
- MCP连接测试
- 真实API调用测试
- 错误处理测试
- 端到端工作流测试

### 步骤6: 验证与测试

- 单元测试（MCP连接）
- 集成测试（真实API调用）
- E2E测试（完整工作流）
- 回归测试（确保无破坏）

---

## 测试文件

**测试文件**: `代码/测试代码/test_enh_07_real_mcp_integration.py`
**对应测试**: ENH-07-01 到 ENH-07-06

**测试策略**:
- 使用条件标记：`@pytest.mark.requires_solidworks`
- 如果SW未运行，跳过真实API测试
- 始终运行错误处理测试

---

## 风险与挑战

### 风险1: SolidWorks未运行

**缓解措施**:
- 启动时检查SW运行状态
- 友好的错误提示
- 可选：自动启动SW（需权限）

### 风险2: API调用超时

**缓解措施**:
- 设置合理的超时时间
- 实现重试机制
- 提供取消选项

### 风险3: 工具参数不匹配

**缓解措施**:
- 详细的工具映射表
- 参数验证和转换
- 测试覆盖所有工具

### 风险4: MCP Server未安装

**缓解措施**:
- 提供安装脚本
- 详细的安装文档
- 降级到mock模式

---

## 依赖项

- **MCP Python SDK**: `pip install mcp`
- **SolidWorks MCP Server**: `SolidworksMCP-python` 目录
- **SolidWorks 2026**: 必须安装并运行
- **pywin32**: Windows COM支持

---

## 成功指标

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| MCP连接成功率 | 100% | 测试用例ENH-07-01 |
| API调用成功率 | ≥95% | 统计成功/失败调用 |
| 端到端工作流成功率 | ≥90% | 测试用例ENH-07-06 |
| 错误处理覆盖率 | 100% | 所有错误场景测试 |
| 性能（API调用） | <2秒 | 平均响应时间 |

---

## 回滚计划

如果真实MCP集成遇到问题：
1. 保留mock模式作为后备
2. 配置项可切换模式
3. 不影响现有功能

```python
# 在coordinator中配置
coordinator = AgentCoordinator(
    use_real_mcp=False,  # 切换回mock
    use_claude=False
)
```

---

## 后续优化

1. **连接池**: 复用MCP连接
2. **异步优化**: 并行调用多个工具
3. **缓存**: 缓存常用操作结果
4. **监控**: 添加性能监控和日志
5. **工具扩展**: 添加更多SolidWorks工具

---

**状态**: 📝 需求定义完成，待实施
**预计工作量**: 4-6小时
**复杂度**: 中等（需要理解MCP协议和SW API）
