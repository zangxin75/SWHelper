# ENH-03: 钣金设计支持 - 增强意图理解

**创建日期**: 2026-04-13
**需求编号**: ENH-03-01 到 ENH-03-06
**对应实施**: Phase 2 - P1优先级增强功能
**优先级**: P1 (高价值功能增强)

---

## 功能描述

增强意图理解和任务分解模块，支持钣金设计相关的自然语言输入，实现：
1. 钣金零件创建识别
2. 折弯特征识别
3. 钣金展开操作
4. 钣金专用特征（凹槽、切口等）
5. 钣金材料识别

---

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-03-01 | 创建钣金零件 | "创建厚度2mm的钣金" | object="PART", parameters={"sheet_metal": True, "thickness": 2} | 识别钣金创建 |
| ENH-03-02 | 添加折弯 | "添加90度折弯" | tasks包含"create_bend", parameters={"angle": 90} | 识别折弯特征 |
| ENH-03-03 | 展开钣金 | "展开钣金" | action="ANALYZE", parameters={"operation": "flatten"} | 识别展开操作 |
| ENH-03-04 | 添加凹槽 | "创建凹槽特征" | tasks包含"create_hem" | 识别凹槽 |
| ENH-03-05 | 钣金切口 | "创建切口" | tasks包含"create_louver" | 识别切口 |
| ENH-03-06 | 钣金材料 | "钣金材料为不锈钢" | parameters={"material": "不锈钢_304"} | 钣金材料识别 |

---

## 验收标准

- 6个测试用例全部通过
- 代码覆盖率 ≥85%
- 钣金关键词识别准确
- 不影响现有PART/ASSEMBLY/DRAWING识别

---

## 技术实现要点

### 1. 意图理解增强

**新增关键词模式** (intent_understanding.py):
```python
# 钣金关键词
self.sheet_metal_patterns = [
    r'钣金|sheet.?metal',
    r'折弯|bend',
    r'展开|flatten',
    r'凹槽|hem',
    r'切口|louver',
    r'厚度|thickness.*mm'
]
```

**参数提取**:
- `thickness`: 钣金厚度（mm）
- `angle`: 折弯角度（度）
- `bend_radius`: 折弯半径（mm）
- `sheet_metal`: 标记为钣金零件（True/False）

### 2. 对象类型扩展

**考虑方案**: 添加SHEET_METAL对象类型

```python
class ObjectType(str, Enum):
    PART = "part"
    ASSEMBLY = "assembly"
    DRAWING = "drawing"
    FEATURE = "feature"
    SHEET_METAL = "sheet_metal"  # 新增
    SKETCH = "sketch"
    UNKNOWN = "unknown"
```

**替代方案**: 使用PART + sheet_metal参数（推荐）
- 优势：减少对象类型复杂度
- 优势：与现有架构兼容
- 劣势：需要参数推断

### 3. 任务分解增强

**新增工具** (task_decomposition.py):
```python
# 钣金相关工具
"create_bend": _create_bend,
"flatten_sheet_metal": _flatten_sheet_metal,
"create_hem": _create_hem,
"create_louver": _create_louver,
```

**任务分解方法**:
```python
def _decompose_create_sheet_metal(self, intent: Intent) -> List[Task]:
    """分解钣金零件创建"""
    params = intent.parameters or {}
    
    # 提取钣金厚度
    thickness = params.get("thickness", 1.0)  # 默认1mm
    
    # 创建基础板
    base_task = self._create_task(
        tool="create_base_flange",
        description=f"Create base flange with thickness {thickness}mm",
        parameters={
            "thickness": thickness,
            "sheet_metal": True
        }
    )
    
    return [base_task]
```

### 4. Mock工具注册

**agent_coordinator.py**:
```python
async def mock_create_bend(**kwargs):
    return {
        "success": True,
        "result": "mock_bend_created",
        "tool_name": "create_bend",
        "execution_time": 0.1
    }

async def mock_flatten_sheet_metal(**kwargs):
    return {
        "success": True,
        "result": "mock_flattened",
        "tool_name": "flatten_sheet_metal",
        "execution_time": 0.15
    }

# 注册工具
self.executor.register_tool("create_bend", mock_create_bend)
self.executor.register_tool("flatten_sheet_metal", mock_flatten_sheet_metal)
self.executor.register_tool("create_hem", mock_create_hem)
self.executor.register_tool("create_louver", mock_create_louver)
```

---

## 钣金设计模式

### 模式1: 创建基础钣金
**输入**: "创建厚度2mm的钣金"
**识别**: action=CREATE, object=PART, sheet_metal=True
**任务**: create_base_flange(thickness=2)

### 模式2: 添加折弯
**输入**: "添加90度折弯"
**识别**: action=MODIFY, feature=bend
**任务**: create_bend(angle=90)

### 模式3: 展开
**输入**: "展开钣金"
**识别**: action=ANALYZE, operation=flatten
**任务**: flatten_sheet_metal()

### 模式4: 复杂钣金
**输入**: "创建钣金，厚度1.5mm，添加2个折弯"
**识别**: 复合指令
**任务**: 
1. create_base_flange(thickness=1.5)
2. create_bend() × 2

---

## 测试文件

**测试文件**: `代码/测试代码/test_enh_03_sheet_metal.py`
**对应测试**: ENH-03-01 到 ENH-03-06

---

## 实施顺序

1. **步骤1**: 扩展关键词模式（意图理解）
2. **步骤2**: 实现钣金参数提取
3. **步骤3**: 添加钣金任务分解方法
4. **步骤4**: 注册mock工具
5. **步骤5**: 编写测试用例
6. **步骤6**: 验证与测试
7. **步骤7**: 回归测试（确保无破坏）

---

**状态**: 📝 需求定义完成，待实施
**预计工作量**: 2-3小时
**复杂度**: 中等（基于现有框架扩展）
