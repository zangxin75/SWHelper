# 需求驱动开发模板 (RDD Template)

**用途**: 本文档是 Claude Code 的开发指令模板。Claude Code 在接手任何开发任务时，必须按照本文档定义的流程执行。

**原则**: 需求表 → 测试代码 → 业务代码。先定义"什么算完成"，再动手写代码。

---

## 流程总览

```
步骤1: 解析项目方案 → 拆分为独立功能模块
步骤2: 为每个模块编写需求表（输入→预期输出的表格）
步骤3: 将需求表自动转化为 pytest 测试用例
步骤4: 运行测试，确认全部为红色（失败）
步骤5: 编写/修改业务代码，逐个让测试变绿
步骤6: 所有测试绿色 = 需求实现完毕
```

---

## 步骤1: 解析项目方案，拆分功能模块

### 规则

1. 读取项目方案文档（技术文档、设计文档等）
2. 识别所有功能点，每个功能点必须是一个**可独立验证**的单元
3. 按依赖关系排序：被依赖的模块排在前面
4. 每个功能模块生成一个需求文件，放在 `文档/需求/` 目录下

### 模块拆分标准

| 条件 | 处理方式 |
|------|---------|
| 一个函数/方法能独立测试 | 拆为一个模块 |
| 多个函数必须一起测试才完整 | 合为一个模块 |
| 功能涉及外部系统（SolidWorks API、Claude API） | 标记为集成模块，需要 mock |
| 功能纯计算/纯逻辑 | 标记为单元模块，不需要 mock |

### 输出格式

每个模块生成一个需求文件，文件名格式：`req_{模块名}.md`

```
文档/需求/
├── req_intent_understanding.md    # 意图理解
├── req_task_decomposition.md      # 任务分解
├── req_task_execution.md          # 任务执行
├── req_result_validation.md       # 结果验证
├── req_knowledge_base.md          # 知识库
└── req_claude_integration.md      # Claude API 集成
```

---

## 步骤2: 编写需求表

### 核心规则

**需求表 = 一张表格，每一行是"给定的输入 + 预期的输出"。**

如果某个需求不能用表格描述"输入什么、期望输出什么"，说明这个需求还不够具体，必须继续拆分或细化。

### 需求表格式

```markdown
## 功能: {模块名称}

**所属模块**: {父模块}
**依赖**: {依赖的其他模块}
**类型**: 单元测试 / 集成测试（需要mock）

### 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| XX-01 | {正常场景} | {具体输入} | {具体预期输出} | |
| XX-02 | {正常场景} | {具体输入} | {具体预期输出} | |
| XX-03 | {边界情况} | {具体输入} | {具体预期输出} | |
| XX-04 | {异常情况} | {具体输入} | {具体预期输出} | |
| XX-05 | {空输入/缺省} | {具体输入} | {具体预期输出} | |
```

### 需求表编写要求

1. **每个需求必须覆盖**:
   - 至少 2 个正常场景
   - 至少 1 个边界场景（空输入、极值、缺失参数）
   - 至少 1 个异常场景（错误输入、不支持的类型）

2. **输入必须是具体的值**，不能写"用户输入"这种模糊描述
   - 对: `"创建一个 100x100x50mm 的铝合金方块"`
   - 错: `"一段创建零件的自然语言"`

3. **预期输出必须是可断言的具体值**，不能写"返回正确结果"
   - 对: `action="create", object="part", parameters={"dimensions":[100,100,50], "material":"铝合金_6061"}`
   - 错: `"返回创建意图"`

4. **编号规则**: 模块缩写 + 序号，如意图理解用 `I-01`，任务分解用 `D-01`

### 本项目已有的模块和编号前缀

| 模块 | 编号前缀 | 需求文件 |
|------|---------|---------|
| 意图理解 (_understand_intent) | I- | req_intent_understanding.md |
| 任务分解 (_decompose_tasks) | D- | req_task_decomposition.md |
| 任务执行 (_execute_task) | E- | req_task_execution.md |
| 结果验证 (_validate_results) | V- | req_result_validation.md |
| 知识库 (_load_knowledge_base) | K- | req_knowledge_base.md |
| Claude API 集成 | C- | req_claude_integration.md |
| Agent 完整流程 (process_design_request) | P- | req_full_pipeline.md |
| 新增模块 | {自定} | req_{name}.md |

---

## 步骤3: 将需求表转化为 pytest 测试

### 转化规则

1. 每个需求文件对应一个测试文件: `req_xxx.md` → `tests/test_xxx.py`
2. 需求表的每一行 → 一个测试用例
3. 使用 `@pytest.mark.parametrize` 将表格转化为参数化测试
4. 测试文件中的注释必须标注对应的需求编号

### 测试文件模板

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模块: {模块名称}
需求文件: 文档/需求/req_{模块名}.md
"""
import pytest
import sys
from pathlib import Path

# 项目路径设置
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "代码" / "Python脚本"))

# ============================================================
# 测试数据 — 直接从需求表复制
# 格式: (编号, 场景描述, 输入, 预期输出)
# ============================================================

TEST_CASES = [
    # ── 正常场景 ──
    (
        "XX-01",
        "场景描述1",
        {输入},
        {预期输出},
    ),
    (
        "XX-02",
        "场景描述2",
        {输入},
        {预期输出},
    ),
    # ── 边界场景 ──
    (
        "XX-03",
        "边界场景",
        {输入},
        {预期输出},
    ),
    # ── 异常场景 ──
    (
        "XX-04",
        "异常场景",
        {输入},
        {预期输出},
    ),
]


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def {fixture_name}():
    """创建被测对象的实例（使用mock模式）"""
    # TODO: 根据实际情况创建fixture
    pass


# ============================================================
# 参数化测试 — 从需求表自动生成
# ============================================================

@pytest.mark.parametrize(
    "case_id, description, input_data, expected",
    TEST_CASES,
    ids=[c[0] for c in TEST_CASES]
)
@pytest.mark.asyncio  # 如果是异步函数需要这个
async def test_{module_name}({fixture_name}, case_id, description, input_data, expected):
    """
    需求编号: {case_id}
    场景: {description}
    """
    # Arrange — 准备（已由fixture完成）

    # Act — 执行
    result = await {fixture_name}.{method_name}(input_data)

    # Assert — 断言
    for key, expected_val in expected.items():
        actual_val = result.get(key) if isinstance(result, dict) else getattr(result, key, None)
        assert actual_val == expected_val, \
            f"{case_id} [{description}]: {key} 期望 {expected_val!r}，实际 {actual_val!r}"
```

### 转化对照表

| 需求表字段 | pytest 代码 |
|-----------|------------|
| 编号列 | `ids=[c[0] for c in TEST_CASES]` |
| 场景描述列 | `description` 参数，失败时用于错误信息 |
| 输入列 | `input_data` 参数 |
| 预期输出列 | `expected` 参数，用字典断言每个字段 |

---

## 步骤4: 运行测试，确认全部为红色

```bash
cd {项目根目录}
pytest tests/ -v --tb=short
```

**期望结果**: 所有测试 FAILED 或 ERROR（因为业务代码还没写或还没改）。

如果此时有测试意外通过了，说明：
1. 需求表描述有误（预期输出写错了）
2. 已有代码恰好满足了这个需求（确认是否真的满足，不是巧合）

---

## 步骤5: 编写业务代码，逐个让测试变绿

### 编码规则

1. **一次只改一个需求**，让一个测试从红变绿
2. **按编号顺序**处理：XX-01 → XX-02 → XX-03 ...
3. 每修好一个测试，立即运行确认：

```bash
pytest tests/test_xxx.py -v -k "XX-01"
```

4. 不要实现需求表以外的功能
5. 最简单的实现优先，不要过度设计

### 编码顺序

对于本项目的 Agent Coordinator:

```
1. 知识库 (K-01~)        ← 无依赖，纯数据
2. 意图理解 (I-01~)       ← 依赖知识库中的材料列表
3. 任务分解 (D-01~)       ← 依赖意图理解的输出格式
4. 任务执行 (E-01~)       ← 依赖任务分解的输出格式，mock MCP 工具
5. 结果验证 (V-01~)       ← 依赖任务执行的输出格式
6. 完整流程 (P-01~)       ← 串起上面所有模块
7. Claude 集成 (C-01~)    ← 依赖完整流程，mock Claude API
```

---

## 步骤6: 全部绿色 = 完成

```bash
# 运行全部测试
pytest tests/ -v

# 确认覆盖率（可选）
pytest tests/ --cov=代码/Python脚本 --cov-report=term-missing
```

**验收标准**: 需求表中的每一行都有对应的测试通过。

---

## 项目目录结构规范

```
D:\sw2026\
│
├── 文档/
│   ├── 需求/                          ← 需求表存放目录
│   │   ├── req_intent_understanding.md
│   │   ├── req_task_decomposition.md
│   │   ├── req_task_execution.md
│   │   ├── req_result_validation.md
│   │   ├── req_knowledge_base.md
│   │   ├── req_claude_integration.md
│   │   └── req_full_pipeline.md
│   ├── 技术文档/
│   ├── 使用指南/
│   └── 项目管理/
│
├── 代码/
│   ├── Python脚本/                    ← 只放业务代码，不放测试
│   │   ├── agent_coordinator.py
│   │   ├── claude_sw_integration.py
│   │   └── ...
│   ├── 测试代码/                      ← 只放测试代码
│   │   ├── conftest.py               ← 共享 fixtures
│   │   ├── test_intent_understanding.py
│   │   ├── test_task_decomposition.py
│   │   ├── test_task_execution.py
│   │   ├── test_result_validation.py
│   │   ├── test_knowledge_base.py
│   │   ├── test_claude_integration.py
│   │   └── test_full_pipeline.py
│   └── VBA宏/
│
├── 配置/
│   └── agent_config.json
│
└── CLAUDE.md                          ← 项目级 Claude Code 指令
```

---

## CLAUDE.md 项目指令

以下内容应追加到项目根目录的 `CLAUDE.md` 文件中：

```markdown
## 开发流程规范（需求驱动开发 RDD）

### 强制规则
1. 任何开发任务必须按 "需求表 → 测试 → 业务代码" 的顺序执行
2. 禁止在没有需求表的情况下编写业务代码
3. 禁止在测试全红之前编写业务代码
4. 需求表存放在 `文档/需求/` 目录，文件名格式 `req_{模块名}.md`
5. 测试代码存放在 `代码/测试代码/` 目录，文件名格式 `test_{模块名}.py`
6. 业务代码存放在 `代码/Python脚本/` 目录，不允许混入测试文件

### 需求表规范
- 每行必须包含: 编号、场景描述、具体输入值、具体预期输出值
- 输入必须是可复现的具体值，不能用模糊描述
- 预期输出必须是可断言的具体值，不能用"正确结果"等模糊表述
- 每个功能至少覆盖: 2个正常场景 + 1个边界场景 + 1个异常场景

### 测试规范
- 使用 pytest + pytest-asyncio
- 使用 @pytest.mark.parametrize 将需求表转化为参数化测试
- 每个测试必须标注对应的需求编号
- 外部依赖（SolidWorks API、Claude API）使用 mock

### 编码规范
- 一次只实现一个需求，按编号顺序
- 最简实现优先
- 不实现需求表以外的功能
```

---

## 快速启动示例

以本项目"意图理解"功能为例，展示完整流程：

### 需求文件: `文档/需求/req_intent_understanding.md`

```markdown
## 功能: 意图理解 (_understand_intent)

**所属模块**: Agent Coordinator
**依赖**: 无
**类型**: 单元测试
**方法签名**: `async _understand_intent(self, user_input: str) -> Dict[str, Any]`

### 返回值结构
```python
{
    "action": str | None,       # "create" | "modify" | "analyze" | "export" | None
    "object": str | None,       # "part" | "assembly" | "drawing" | None
    "parameters": {
        "dimensions": list[float],   # mm为单位，[长, 宽, 高]
        "material": str | None,      # 材料名称
    },
    "constraints": list           # 约束条件（暂未实现）
}
```

### 需求表

| 编号 | 场景描述 | 输入 (user_input) | 预期 action | 预期 object | 预期 parameters |
|------|---------|------------------|------------|------------|----------------|
| I-01 | 创建零件+尺寸+材料 | "创建一个 100x100x50mm 的铝合金方块" | "create" | "part" | dimensions=[100,100,50], material="铝合金_6061" |
| I-02 | 创建零件+尺寸 | "新建一个 200x150x30mm 的零件" | "create" | "part" | dimensions=[200,150,30], material=None |
| I-03 | 创建装配体 | "创建一个装配体" | "create" | "assembly" | dimensions=[], material=None |
| I-04 | 创建工程图 | "画一个工程图" | "create" | "drawing" | dimensions=[], material=None |
| I-05 | 设计（同义词） | "设计一个支架" | "create" | "part" | dimensions=[], material=None |
| I-06 | 修改操作 | "修改零件的圆角为5mm" | "modify" | "part" | dimensions=[], material=None |
| I-07 | 分析操作 | "分析当前零件的质量" | "analyze" | None | dimensions=[], material=None |
| I-08 | 导出操作 | "导出STEP格式文件" | "export" | None | dimensions=[], material=None |
| I-09 | 省略关键词的创建 | "100x50x30mm 不锈钢方块" | "create" | "part" | dimensions=[100,50,30], material="不锈钢_304" |
| I-10 | 空输入 | "" | None | None | dimensions=[], material=None |
| I-11 | 不支持的操作 | "删除这个零件" | None | None | dimensions=[], material=None |
| I-12 | 单位转换-厘米 | "创建一个 10x10x5厘米 的方块" | "create" | "part" | dimensions=[100,100,50], material=None |
| I-13 | 材料同义词 | "创建一个铝合金零件" | "create" | "part" | dimensions=[], material="铝合金_6061" |
| I-14 | 两个尺寸默认厚度 | "创建一个 100x50mm 的方块" | "create" | "part" | dimensions=[100,50,10], material=None |
| I-15 | 单尺寸三向相同 | "创建一个 50mm 的方块" | "create" | "part" | dimensions=[50,50,50], material=None |
```

### 测试文件: `代码/测试代码/test_intent_understanding.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模块: 意图理解
需求文件: 文档/需求/req_intent_understanding.md
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Python脚本"))

from agent_coordinator import SolidWorksAgentCoordinator


# ============================================================
# 测试数据 — 需求表 I-01 ~ I-15
# ============================================================

INTENT_CASES = [
    # ── 正常场景 ──
    ("I-01", "创建+尺寸+材料", "创建一个 100x100x50mm 的铝合金方块",
     "create", "part", {"dimensions": [100, 100, 50], "material": "铝合金_6061"}),
    ("I-02", "创建+尺寸无材料", "新建一个 200x150x30mm 的零件",
     "create", "part", {"dimensions": [200, 150, 30], "material": None}),
    ("I-03", "创建装配体", "创建一个装配体",
     "create", "assembly", {"dimensions": [], "material": None}),
    ("I-04", "创建工程图", "画一个工程图",
     "create", "drawing", {"dimensions": [], "material": None}),
    ("I-05", "设计同义词", "设计一个支架",
     "create", "part", {"dimensions": [], "material": None}),
    ("I-06", "修改操作", "修改零件的圆角为5mm",
     "modify", "part", {"dimensions": [], "material": None}),
    ("I-07", "分析操作", "分析当前零件的质量",
     "analyze", None, {"dimensions": [], "material": None}),
    ("I-08", "导出操作", "导出STEP格式文件",
     "export", None, {"dimensions": [], "material": None}),
    ("I-09", "省略关键词", "100x50x30mm 不锈钢方块",
     "create", "part", {"dimensions": [100, 50, 30], "material": "不锈钢_304"}),

    # ── 边界场景 ──
    ("I-10", "空输入", "",
     None, None, {"dimensions": [], "material": None}),
    ("I-12", "厘米单位转换", "创建一个 10x10x5厘米 的方块",
     "create", "part", {"dimensions": [100, 100, 50], "material": None}),
    ("I-14", "两尺寸默认厚度", "创建一个 100x50mm 的方块",
     "create", "part", {"dimensions": [100, 50, 10], "material": None}),
    ("I-15", "单尺寸三向相同", "创建一个 50mm 的方块",
     "create", "part", {"dimensions": [50, 50, 50], "material": None}),

    # ── 异常场景 ──
    ("I-11", "不支持的操作", "删除这个零件",
     None, None, {"dimensions": [], "material": None}),
]


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def coordinator():
    return SolidWorksAgentCoordinator(use_mock=True)


# ============================================================
# 参数化测试
# ============================================================

@pytest.mark.parametrize(
    "case_id, desc, user_input, expected_action, expected_object, expected_params",
    INTENT_CASES,
    ids=[c[0] for c in INTENT_CASES],
)
@pytest.mark.asyncio
async def test_understand_intent(
    coordinator, case_id, desc, user_input,
    expected_action, expected_object, expected_params
):
    """
    需求编号: {case_id}
    场景: {desc}
    """
    intent = await coordinator._understand_intent(user_input)

    assert intent["action"] == expected_action, \
        f"{case_id} [{desc}]: action 期望 '{expected_action}'，实际 '{intent['action']}'"

    assert intent["object"] == expected_object, \
        f"{case_id} [{desc}]: object 期望 '{expected_object}'，实际 '{intent['object']}'"

    for key, expected_val in expected_params.items():
        actual_val = intent["parameters"].get(key)
        assert actual_val == expected_val, \
            f"{case_id} [{desc}]: parameters.{key} 期望 {expected_val!r}，实际 {actual_val!r}"
```

### 执行流程

```bash
# 1. 跑测试，确认全红
pytest 代码/测试代码/test_intent_understanding.py -v

# 2. 逐个修，每次确认多一个绿
pytest 代码/测试代码/test_intent_understanding.py -v -k "I-01"
# ... 修改 _understand_intent 代码 ...
pytest 代码/测试代码/test_intent_understanding.py -v -k "I-02"
# ... 重复 ...

# 3. 全部通过
pytest 代码/测试代码/test_intent_understanding.py -v
```

---

## 检查清单

Claude Code 在完成每个模块后，必须逐项确认：

- [ ] 需求表已创建，且每行有具体的输入和预期输出
- [ ] 需求表覆盖了正常、边界、异常场景
- [ ] 测试文件已创建，与需求表一一对应
- [ ] 所有需求编号在测试 ids 中正确标注
- [ ] 运行测试，需求表中的每行都有对应测试通过
- [ ] 没有实现需求表以外的功能
- [ ] 测试文件在 `代码/测试代码/` 目录，业务代码在 `代码/Python脚本/` 目录
