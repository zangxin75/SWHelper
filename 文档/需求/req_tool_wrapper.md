# 功能: 工具调用封装模块

**所属模块**: 第一阶段 - 基础Agent框架
**依赖**: SolidWorks MCP适配器
**类型**: 集成测试 (需mock MCP适配器)
**文件**: `代码/Python脚本/tool_wrapper.py`

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| T-01 | 初始化工具包装器(mock模式) | {"use_mock": true} | ToolWrapper实例, adapter为MockAdapter | |
| T-02 | 初始化工具包装器(真实模式) | {"use_mock": false} | ToolWrapper实例, adapter为SWAdapter | |
| T-03 | 调用存在的工具(mock) | {"tool": "create_part", "params": {"template": "part"}, "mock": true} | {"success": true, "result": {...}} | |
| T-04 | 调用不存在的工具 | {"tool": "unknown_tool", "params": {}, "mock": true} | {"success": false, "error": "Tool not found"} | 异常场景 |
| T-05 | 列出所有可用工具 | {} | 工具列表长度>0,包含"create_part"等 | |
| T-06 | 工具调用超时处理 | {"tool": "slow_tool", "timeout": 1} | {"success": false, "error": "Timeout"} | 边界场景 |
| T-07 | 工具调用自动重试 | {"tool": "flaky_tool", "retries": 3} | 重试3次后成功或失败 | |
| T-08 | 参数验证失败 | {"tool": "create_part", "params": null} | {"success": false, "error": "Invalid parameters"} | 异常场景 |
