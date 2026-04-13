# ENH-01: 意图理解 - 装配体设计支持

**创建日期**: 2026-04-13
**需求编号**: ENH-01-01 到 ENH-01-06
**对应实施**: Phase 2 - 增强现有模块功能
**优先级**: P1 (高价值增强)

---

## 功能描述

扩展意图理解和任务分解模块，支持装配体（Assembly）设计操作，包括：
- 创建装配体
- 插入配合（Mate）
- 干涉检查
- 爆炸视图
- 装配体材料设置
- 子装配体支持

---

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-01-01 | 创建装配体 | "创建一个装配体，包含3个零件" | object="ASSEMBLY", parameters={"component_count": 3} | 识别装配体创建 |
| ENH-01-02 | 插入配合 | "添加同轴配合" | action="MODIFY", object="ASSEMBLY", parameters={"mate_type": "coaxial"} | 识别配合操作 |
| ENH-01-03 | 干涉检查 | "检查装配体干涉" | action="ANALYZE", object="ASSEMBLY", parameters={"check_type": "interference"} | 识别分析指令 |
| ENH-01-04 | 爆炸视图 | "创建爆炸视图" | action="MODIFY", object="ASSEMBLY", parameters={"view_type": "exploded"} | 识别爆炸视图 |
| ENH-01-05 | 装配体材料 | "装配体材料为铝合金" | parameters={"material": "铝合金_6061"} | 装配体材料设置 |
| ENH-01-06 | 子装配体 | "创建子装配体" | object="ASSEMBLY", parameters={"is_subassembly": True} | 子装配体识别 |

---

## 验收标准

- 6个测试用例全部通过
- 支持 ASSEMBLY 对象类型
- 代码覆盖率 ≥90%
- 与现有 PART 设计流程兼容

---

## 技术实现要点

### 1. Schema 扩展
- 在 `ObjectType` 枚举中添加 `ASSEMBLY` 类型
- 支持装配体特有参数（component_count, mate_type, check_type, view_type, is_subassembly）

### 2. 意图理解扩展
- 添加装配体关键词：装配体、组件、配合、干涉、爆炸
- 添加配合类型关键词：同轴、重合、平行、垂直、距离、角度
- 扩展 `_match_object()` 方法

### 3. 任务分解扩展
- 添加 `_decompose_create_assembly()` 方法
- 添加 `_decompose_add_mate()` 方法
- 添加 `_decompose_check_interference()` 方法
- 添加 `_decompose_create_exploded_view()` 方法

### 4. 工具注册（Mock）
- `create_assembly`: 创建装配体
- `add_mate`: 添加配合
- `check_interference`: 检查干涉
- `create_exploded_view`: 创建爆炸视图

---

## 测试文件

- **测试文件**: `代码/测试代码/test_enh_01_assembly_design.py`
- **对应测试**: ENH-01-01 到 ENH-01-06
- **E2E测试**: E2E-17 到 E2E-20

---

## 实施顺序

1. **步骤1**: 扩展 Schema（ObjectType 枚举）
2. **步骤2**: 意图理解模块扩展
3. **步骤3**: 任务分解模块扩展
4. **步骤4**: Coordinator 工具注册
5. **步骤5**: 编写测试用例
6. **步骤6**: 验证与测试

---

**状态**: 📝 需求定义完成，待实施
