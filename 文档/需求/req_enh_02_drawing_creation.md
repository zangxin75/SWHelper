# ENH-02: 意图理解 - 工程图创建支持

**创建日期**: 2026-04-13
**需求编号**: ENH-02-01 到 ENH-02-06
**对应实施**: Phase 2 - 增强现有模块功能
**优先级**: P1 (高价值增强)

---

## 功能描述

扩展意图理解和任务分解模块，支持工程图（Drawing）设计操作，包括：
- 创建工程图
- 添加尺寸标注
- 添加注释
- 导出PDF
- 图纸格式设置
- 比例设置

---

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-02-01 | 创建工程图 | "创建工程图，3个视图" | object="DRAWING", parameters={"view_count": 3} | 识别工程图创建 |
| ENH-02-02 | 添加尺寸 | "添加所有尺寸" | action="MODIFY", object="DRAWING", parameters={"annotation": "dimensions"} | 识别尺寸标注 |
| ENH-02-03 | 添加注释 | "添加技术要求注释" | action="MODIFY", object="DRAWING", parameters={"annotation": "note"} | 识别注释 |
| ENH-02-04 | 导出PDF | "导出工程图为PDF" | action="EXPORT", object="DRAWING", parameters={"format": "pdf"} | 识别PDF导出 |
| ENH-02-05 | 图纸格式 | "使用A3图纸" | parameters={"sheet_format": "A3"} | 识别图纸格式 |
| ENH-02-06 | 比例设置 | "比例1:2" | parameters={"scale": "1:2"} | 识别比例 |

---

## 验收标准

- 6个测试用例全部通过
- 支持 DRAWING 对象类型
- 代码覆盖率 ≥85%
- 与现有 PART/ASSEMBLY 设计流程兼容

---

## 技术实现要点

### 1. Schema 扩展
- 在 `ObjectType` 枚举中添加 `DRAWING` 类型
- 支持工程图特有参数（view_count, annotation, sheet_format, scale）

### 2. 意图理解扩展
- 添加工程图关键词：工程图、图纸、视图、尺寸、标注、注释、PDF
- 添加图纸格式关键词：A0, A1, A2, A3, A4
- 添加比例关键词：1:1, 1:2, 2:1 等
- 扩展 `_match_object()` 方法

### 3. 任务分解扩展
- 添加 `_decompose_create_drawing()` 方法
- 添加 `_decompose_add_dimensions()` 方法
- 添加 `_decompose_add_annotation()` 方法
- 添加 `_decompose_export_drawing()` 方法

### 4. 工具注册（Mock）
- `create_drawing`: 创建工程图
- `add_dimensions`: 添加尺寸
- `add_annotation`: 添加注释
- `export_drawing_pdf`: 导出PDF

---

## 测试文件

- **测试文件**: `代码/测试代码/test_enh_02_drawing_creation.py`
- **对应测试**: ENH-02-01 到 ENH-02-06
- **E2E测试**: E2E-21 到 E2E-24

---

## 实施顺序

1. **步骤1**: 扩展 Schema（ObjectType 枚举添加 DRAWING）
2. **步骤2**: 意图理解模块扩展
3. **步骤3**: 任务分解模块扩展
4. **步骤4**: Coordinator 工具注册
5. **步骤5**: 编写测试用例
6. **步骤6**: 验证与测试

---

**状态**: 📝 需求定义完成，待实施
