# 🚀 SolidWorks AI Agent 使用指南

**版本**: 1.0
**更新日期**: 2026-04-12
**适用对象**: SolidWorks用户、开发工程师、CAE分析师

---

## 🎯 快速开始

### 前置条件

- ✅ SolidWorks 2026 已安装
- ✅ Python 3.11+ 已安装
- ✅ （可选）Claude API 密钥

### 一键部署

```bash
# 1. 运行部署脚本
双击: 部署Agent.bat

# 2. 等待依赖安装完成
# 3. 部署完成后会出现启动选项
```

### 立即体验

```bash
# 方式1: 基础Agent（无需API密钥）
双击: 启动基础Agent.bat

# 方式2: Claude增强Agent
双击: 启动Claude增强Agent.bat

# 方式3: 运行测试
双击: 运行测试.bat
```

---

## 📖 使用指南

### 基础模式使用

**启动**:
```bash
双击: 启动基础Agent.bat
```

**使用示例**:

#### 1. 创建简单零件

```
👤 您: 创建一个 100x100x50mm 的铝合金方块

🤖 Agent:
✅ 设计任务完成!

执行的操作:
  ✅ 创建新零件文档
  ✅ 创建 100x100 矩形草图
  ✅ 拉伸 50mm
  ✅ 设置材料为 铝合金_6061
```

#### 2. 创建圆柱体

```
👤 您: 创建一个 直径50高100的圆柱

🤖 Agent:
✅ 设计任务完成!

执行的操作:
  ✅ 创建新零件文档
  ✅ 创建直径50的圆形草图
  ✅ 拉伸 100mm
  ✅ 设置默认材料
```

#### 3. 分析零件质量

```
👤 您: 分析当前零件的质量

🤖 Agent:
✅ 分析完成!

质量属性:
  - 质量: 0.54 kg
  - 体积: 200000 mm³
  - 密度: 2.7 g/cm³
  - 材料: 铝合金_6061
```

### Claude增强模式使用

**启动**:
```bash
# 1. 设置API密钥
set ANTHROPIC_API_KEY=your-key-here

# 2. 启动Claude增强版本
双击: 启动Claude增强Agent.bat
```

**优势**:
- 🧠 更智能的理解能力
- 📝 详细的设计建议
- 🔧 优化方案提供
- 🎓 设计知识库支持

**使用示例**:

#### 1. 复杂设计任务

```
👤 您: 设计一个轴承座，底座200x150x20mm，支撑高度100mm，
       顶部有直径50mm的轴承孔，两侧有M10安装孔

🤖 Claude: 理解了，这是一个轴承座设计。让我为您分析：

## 设计理解
这是一个典型的轴承座设计，包含：
- 底座: 200x150x20mm，用于安装固定
- 支撑: 高度100mm，连接底座和轴承
- 轴承孔: 直径50mm，用于安装轴承
- 安装孔: M10，用于固定轴承座

## 操作步骤
1. 创建新零件文档
2. 绘制底座矩形草图（200x150）
3. 拉伸20mm创建底座
4. 在顶部绘制支撑轮廓
5. 拉伸100mm创建支撑
6. 创建轴承孔（直径50mm，贯穿支撑）
7. 在底座两侧创建M10安装孔
8. 添加适当的圆角（R3-R5）
9. 设置材料（推荐碳钢Q235）

## 设计建议
- 考虑在底座添加加强筋提高刚性
- 支撑与底座连接处添加圆角减少应力集中
- 轴承孔可以考虑使用轴套便于维修
- 安装孔建议使用沉头孔改善外观

[自动执行SolidWorks操作...]

✅ 设计完成！已创建轴承座零件
```

#### 2. 设计优化

```
👤 您: 这个支架太重了，帮我优化到2kg以内

🤖 Claude: 我来帮您优化这个支架设计。

## 当前分析
- 质量: 2.5kg
- 材料: 铝合金6061
- 主要问题: 实心结构导致重量过大

## 优化方案
1. 在支撑部分添加减重槽（宽度30mm）
2. 使用薄壁结构（壁厚3mm）
3. 在非关键区域去除材料
4. 保留关键结构强度

## 预期效果
- 预计质量: 1.8kg（减少28%）
- 强度保持: 90%以上
- 制造可行性: 良好

[执行优化操作...]

✅ 优化完成！
- 原质量: 2.5kg
- 新质量: 1.78kg
- 减重: 28.8%
```

### 批量处理模式

**创建批量任务文件** (`配置/batch_tasks.txt`):

```
创建一个 50x50x20mm 的方块
创建一个 直径30高50的圆柱
分析当前零件的质量
导出STEP格式文件
```

**运行批量处理**:

```python
# 创建批量处理脚本
import asyncio
from agent_coordinator import SolidWorksAgentCoordinator

async def batch_process():
    coordinator = SolidWorksAgentCoordinator(use_mock=False)

    # 读取任务文件
    with open('配置/batch_tasks.txt', 'r', encoding='utf-8') as f:
        tasks = [line.strip() for line in f if line.strip()]

    # 执行批量任务
    results = []
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] {task}")
        result = await coordinator.process_design_request(task)
        results.append(result)

    # 输出结果
    success_count = sum(1 for r in results if r["success"])
    print(f"\n批量处理完成: {success_count}/{len(tasks)}")

asyncio.run(batch_process())
```

---

## 🎓 高级功能

### 1. 自定义设计知识库

编辑 `配置/agent_config.json`:

```json
{
  "knowledge_base": {
    "materials": {
      "自定义材料": {
        "density": 7.85,
        "yield_strength": 355,
        "typical_uses": ["特殊应用"]
      }
    }
  }
}
```

### 2. 自定义设计模板

```python
# 在agent_coordinator.py中添加
custom_templates = {
    "custom_part": {
        "parameters": {...},
        "operations": [...]
    }
}
```

### 3. 集成到现有工作流

```python
# 在您的Python脚本中调用
from agent_coordinator import SolidWorksAgentCoordinator

async def automated_design():
    agent = SolidWorksAgentCoordinator()
    
    # 自动化设计流程
    result = await agent.process_design_request(
        "创建标准支架零件"
    )
    
    return result
```

---

## 🔧 配置说明

### Agent配置

**配置文件**: `配置/agent_config.json`

**主要设置**:

```json
{
  "agent_settings": {
    "default_material": "铝合金_6061",
    "default_units": "mm",
    "enable_validation": true,
    "max_retries": 3
  },
  "claude_settings": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 2048,
    "fallback_to_local": true
  }
}
```

### 日志配置

**日志文件**: `配置/agent.log`

**查看日志**:
```bash
tail -f 配置/agent.log
```

---

## 💡 最佳实践

### 1. 明确的设计描述

**❌ 不好的描述**:
```
"做一个零件"
"设计一个东西"
```

**✅ 好的描述**:
```
"创建一个 100x100x50mm 的铝合金方块"
"设计一个轴承座，底座200x150x20mm，支撑高度100mm"
```

### 2. 使用标准术语

**推荐的术语**:
- ✅ 拉伸、旋转、扫描
- ✅ 圆角、倒角、拔模
- ✅ 装配、配合、阵列
- ✅ M6、M8、M10（标准螺栓规格）

### 3. 分步骤描述复杂设计

**复杂设计**:
```
第1步: 创建底座，200x150x20mm
第2步: 在顶部创建支撑，高度100mm
第3步: 创建轴承孔，直径50mm
第4步: 两侧添加M10安装孔
```

### 4. 利用设计知识库

**内置知识**:
- 材料属性（密度、强度）
- 设计规则（壁厚、圆角）
- 标准件规格（螺栓、轴承）

---

## 🐛 故障排除

### 常见问题

#### 1. Agent无法连接SolidWorks

**症状**: Agent显示连接失败

**解决方法**:
```bash
# 1. 确保SolidWorks 2026正在运行
# 2. 检查COM接口
# 3. 以管理员身份运行Agent
```

#### 2. Claude API调用失败

**症状**: 显示API调用错误

**解决方法**:
```bash
# 1. 检查API密钥是否正确
echo %ANTHROPIC_API_KEY%

# 2. 系统会自动切换到本地模式
# 无需API密钥也能使用基础功能
```

#### 3. 工具调用失败

**症状**: 某些操作无法执行

**解决方法**:
```bash
# 1. 运行测试脚本诊断问题
双击: 运行测试.bat

# 2. 查看日志文件
type 配置\agent.log

# 3. 检查MCP服务器状态
```

---

## 📊 性能优化

### 加速执行

**并行处理**:
```python
# 在配置中启用并行处理
"parallel_execution": true,
"max_parallel_tasks": 5
```

**缓存机制**:
```python
# 启用结果缓存
"enable_caching": true,
"cache_size": 100
```

---

## 🎯 应用场景

### 1. 快速原型设计

```
"创建一个连接器模型，一端是M8螺纹，另一端是M6螺纹，
长度50mm，中间有法兰"
```

### 2. 批量零件生成

```python
# 批量生成标准件
sizes = ["M3", "M4", "M5", "M6", "M8"]
for size in sizes:
    await agent.process_design_request(
        f"创建标准六角螺母 {size}"
    )
```

### 3. 设计优化

```
"优化这个支架，在保持强度的前提下减轻30%重量"
```

### 4. 自动化文档生成

```
"为当前零件创建工程图，包含主视图、俯视图和侧视图，
添加主要尺寸和技术要求"
```

---

## 📞 获取帮助

### 文档资源

- 📖 [实施方案](../Claude_Code_SolidWorks_Agent_实施方案.md)
- 📋 [研究报告](../文档/研究报告/SolidWorks_2026_AI_Agent_自动化研究报告.md)
- 🔧 [配置说明](./agent_config.json)

### 技术支持

**遇到问题?**
1. 查看 [使用指南](.)
2. 运行 [测试脚本](../代码/测试代码/test_agent.py)
3. 查看日志文件 `配置/agent.log`

---

## 🎉 下一步

### 学习资源

1. **基础教程**: 运行基础Agent，尝试简单的零件创建
2. **进阶教程**: 使用Claude增强模式，体验智能设计
3. **API文档**: 阅读MCP服务器文档，了解可用工具
4. **实战项目**: 将Agent集成到您的实际工作流程

### 扩展开发

1. **添加新技能**: 在Agent中添加自定义设计逻辑
2. **集成企业系统**: 连接PLM、ERP等系统
3. **构建知识库**: 积累企业特定的设计知识
4. **开发自定义UI**: 创建图形界面

---

**维护者**: Claude Code AI Assistant
**版本**: 1.0
**最后更新**: 2026-04-12

---

<div align="center">

### 🚀 开始您的AI驱动设计之旅！

</div>
