# Claude API 集成测试指南

**创建日期**: 2026-04-13
**目的**: 验证真实Claude API的表现和本地模式的对比

---

## 快速开始

### 1. 获取API密钥

访问 [Anthropic Console](https://console.anthropic.com/) 并：
1. 注册/登录账号
2. 进入 API Keys 页面
3. 创建新的API密钥
4. 复制密钥（格式类似: `sk-ant-api03-...`）

### 2. 配置环境变量

**Windows (PowerShell)**:
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

**Windows (CMD)**:
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Linux/Mac (Bash)**:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

### 3. 运行测试

```bash
cd D:\sw2026
python 代码/测试代码/test_claude_simple.py
```

---

## 测试结果对比（本地模式）

### 测试用例1: 复杂零件设计

**输入**:
```
设计一个轴承座，底座200x150x20mm，支撑高度100mm，顶部有直径50mm的孔，使用45号钢
```

**本地模式结果**:
- Action: modify (识别为修改操作)
- Object: feature (识别为特征)
- Confidence: 0.91
- Parameters:
  - dimensions: [200.0, 150.0, 20.0]
  - material: 铸铁_普通
  - feature_type: hole
  - diameter: 50.0

**分析**:
- ✅ 成功提取尺寸参数
- ✅ 成功提取孔径
- ✅ 识别材料
- ⚠️ Action识别为modify而非create（因为"孔"操作）
- ⚠️ Object识别为feature而非part（因为提到了特征）

**预期Claude改进**:
- Action应识别为create（创建整个零件）
- Object应识别为part（零件级别）
- 应提取support_height参数（当前缺失）
- 应提取type=bearing_seat（零件类型）

---

### 测试用例2: 工程图创建

**输入**:
```
创建一个工程图，使用A3图纸，1:2比例，包含3个视图
```

**本地模式结果**:
- Action: create
- Object: drawing
- Confidence: 0.71
- Parameters:
  - view_count: 3
  - sheet_format: A3
  - scale: 1:2

**分析**:
- ✅ 完美识别所有参数
- ✅ Action和Object正确
- ⚠️ 置信度中等（0.71）

**预期Claude改进**:
- 置信度应更高（>0.9）
- 参数提取应该相同（已经很完美）

---

### 测试用例3: 装配体设计

**输入**:
```
创建一个装配体，包含5个零件，使用同轴配合，检查干涉
```

**本地模式结果**:
- Action: create
- Object: assembly
- Confidence: 0.77
- Parameters:
  - component_count: 5
  - mate_type: coaxial
  - check_type: interference

**分析**:
- ✅ 完美识别所有参数
- ✅ Action和Object正确
- ✅ 置信度良好（0.77）

**预期Claude改进**:
- 置信度可能提升到0.9+
- 参数提取应该相同

---

### 测试用例4: 修改操作

**输入**:
```
修改这个零件，把高度从100mm改成150mm
```

**本地模式结果**:
- Action: modify
- Object: part
- Confidence: 0.68
- Parameters: (无)

**分析**:
- ✅ Action和Object正确
- ⚠️ 置信度较低（0.68）
- ❌ 未提取修改的参数（from/to值）

**预期Claude改进**:
- 应提取参数名：height
- 应提取原值：100
- 应提取新值：150
- 置信度应该提升

---

### 测试用例5: 导出操作

**输入**:
```
把这个工程图导出为PDF格式
```

**本地模式结果**:
- Action: export
- Object: drawing
- Confidence: 0.66
- Parameters:
  - format: pdf

**分析**:
- ✅ 完美识别操作和格式
- ⚠️ 置信度较低（0.66）

**预期Claude改进**:
- 置信度应该提升到0.9+
- 参数提取应该相同

---

## 性能对比预期

| 维度 | 本地模式 | Claude API模式 |
|------|---------|---------------|
| 响应速度 | 快（<10ms） | 慢（500-2000ms） |
| 置信度 | 中等（0.6-0.9） | 高（0.9-0.99） |
| 参数提取 | 基础参数 | 完整参数 |
| 复杂场景 | 有限支持 | 强大支持 |
| 成本 | 免费 | 按API调用计费 |
| 可靠性 | 100%（离线） | 依赖网络 |

---

## 预期Claude API优势

### 1. 更精确的意图识别

**场景**: "设计一个轴承座"
- **本地**: 可能识别为modify+feature（因为有"孔"）
- **Claude**: 正确识别为create+part

### 2. 更完整的参数提取

**场景**: "底座200x150x20mm，支撑高度100mm"
- **本地**: 只提取dimensions=[200,150,20]
- **Claude**: 提取base_dimensions和support_height两个独立参数

### 3. 更好的上下文理解

**场景**: "修改这个零件，把高度从100mm改成150mm"
- **本地**: 无法提取from/to值
- **Claude**: 提取parameter_name=height, old_value=100, new_value=150

### 4. 更高的置信度

- **本地**: 0.6-0.9（取决于规则匹配度）
- **Claude**: 0.9-0.99（基于语义理解）

---

## 测试建议

### 第一阶段: 本地模式基线
- ✅ 已完成（上文测试结果）
- 了解本地模式的能力和局限

### 第二阶段: Claude API测试（需要API密钥）
1. 配置API密钥
2. 运行test_claude_simple.py
3. 对比两种模式的结果
4. 记录改进点

### 第三阶段: 混合模式验证
1. 测试API失败时的降级
2. 测试安全过滤
3. 测试超时处理

---

## 故障排查

### 问题1: ModuleNotFoundError

**症状**: `ModuleNotFoundError: No module named 'intent_understanding'`

**解决**:
```bash
# 确认当前目录
cd D:\sw2026

# 使用绝对路径运行
python 代码/测试代码/test_claude_simple.py
```

### 问题2: API初始化失败

**症状**: `Warning: anthropic package not installed`

**解决**:
```bash
pip install anthropic
```

### 问题3: API调用超时

**症状**: `TimeoutError` 或 `API timeout`

**解决**:
- 检查网络连接
- 检查API密钥是否有效
- 系统会自动降级到本地模式

### 问题4: 中文显示乱码

**症状**: 控制台显示乱码

**说明**: 功能正常，仅显示问题。不影响测试结果。

**解决**（可选）:
```bash
# Windows PowerShell
chcp 65001
python 代码/测试代码/test_claude_simple.py
```

---

## 下一步行动

### 如果有API密钥：
1. ✅ 配置环境变量
2. ✅ 运行测试脚本
3. ✅ 对比结果
4. ✅ 记录改进

### 如果没有API密钥：
1. 📝 上文已展示本地模式能力
2. 📝 可以参考预期改进点
3. 📝 决定是否申请API密钥

---

**更新时间**: 2026-04-13
**联系方式**: 如有问题请查看项目文档
