# Task Decomposition Module Requirements

## Module Overview
将用户意图分解为可执行的 SolidWorks API 任务序列。

## Requirements Table

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| D-01 | CREATE 意图分解 - 创建立方体 | Intent(action="CREATE", entity="PART", params={"name": "test", "type": "cube", "width": 10, "height": 20, "depth": 30}) | Task列表: [Task(tool="create_part", params={"name": "test"}), Task(tool="create_sketch", params={"plane": "Front"}), Task(tool="create_rectangle", params={"width": 10, "height": 20}), Task(tool="extrude_boss", params={"depth": 30, "direction": "blind"})] | 依赖关系: create_sketch 依赖 create_part, create_rectangle 依赖 create_sketch, extrude_boss 依赖 create_rectangle |
| D-02 | CREATE 意图分解 - 创建圆柱 | Intent(action="CREATE", entity="PART", params={"name": "cylinder", "type": "cylinder", "diameter": 15, "height": 40}) | Task列表: [Task(tool="create_part", params={"name": "cylinder"}), Task(tool="create_sketch", params={"plane": "Front"}), Task(tool="create_circle", params={"diameter": 15}), Task(tool="extrude_boss", params={"depth": 40, "direction": "blind"})] | 依赖关系同上 |
| D-03 | MODIFY 意图分解 - 修改尺寸 | Intent(action="MODIFY", entity="DIMENSION", params={"feature": "Sketch1", "dimension": "D1", "value": 50.0}) | Task列表: [Task(tool="modify_dimension", params={"feature": "Sketch1", "dimension": "D1", "value": 50.0})] | 无依赖 |
| D-04 | MODIFY 意图分解 - 修改特征参数 | Intent(action="MODIFY", entity="FEATURE", params={"name": "Extrude1", "depth": 25.0}) | Task列表: [Task(tool="modify_feature", params={"name": "Extrude1", "depth": 25.0})] | 无依赖 |
| D-05 | ANALYZE 意图分解 - 测量体积 | Intent(action="ANALYZE", entity="PART", params={"metric": "volume"}) | Task列表: [Task(tool="get_mass_properties", params={})] | 无依赖 |
| D-06 | ANALYZE 意图分解 - 测量距离 | Intent(action="ANALYZE", entity="GEOMETRY", params={"type": "distance", "entity1": "Point1@Sketch1", "entity2": "Point2@Sketch1"}) | Task列表: [Task(tool="measure_distance", params={"entity1": "Point1@Sketch1", "entity2": "Point2@Sketch1"})] | 无依赖 |
| D-07 | EXPORT 意图分解 - 导出 STEP | Intent(action="EXPORT", entity="PART", params={"format": "step", "filepath": "C:/temp/test.step"}) | Task列表: [Task(tool="export_file", params={"format": "step", "filepath": "C:/temp/test.step"})] | 无依赖 |
| D-08 | EXPORT 意图分解 - 导出 PDF 图纸 | Intent(action="EXPORT", entity="DRAWING", params={"format": "pdf", "filepath": "C:/temp/drawing.pdf"}) | Task列表: [Task(tool="export_drawing", params={"format": "pdf", "filepath": "C:/temp/drawing.pdf"})] | 无依赖 |
| D-09 | 边界场景 - 缺少必需参数 | Intent(action="CREATE", entity="PART", params={"name": "test", "type": "cube"}) | 抛出 ValueError 异常，消息包含 "Missing required parameter" | 缺少 width, height, depth |
| D-10 | 边界场景 - 未知实体类型 | Intent(action="CREATE", entity="ASSEMBLY", params={}) | 抛出 ValueError 异常，消息包含 "Unknown entity type" | ASSEMBLY 暂不支持 |
| D-11 | 边界场景 - 未知动作类型 | Intent(action="DELETE", entity="PART", params={}) | 抛出 ValueError 异常，消息包含 "Unknown action type" | DELETE 不支持 |
| D-12 | 边界场景 - 零尺寸 | Intent(action="CREATE", entity="PART", params={"name": "zero", "type": "cube", "width": 0, "height": 10, "depth": 10}) | 抛出 ValueError 异常，消息包含 "Dimension must be positive" | 零尺寸无效 |
| D-13 | 任务依赖顺序 - 立方体 | 同 D-01 | 任务执行顺序: [create_part, create_sketch, create_rectangle, extrude_boss] | 验证依赖关系正确 |
| D-14 | 任务依赖顺序 - 圆柱 | 同 D-02 | 任务执行顺序: [create_part, create_sketch, create_circle, extrude_boss] | 验证依赖关系正确 |
| D-15 | 并行任务 - 多个测量任务 | Intent(action="ANALYZE", entity="PART", params={"metrics": ["volume", "area", "mass"]}) | Task列表: [Task(tool="get_mass_properties", params={}), Task(tool="get_surface_area", params={}), Task(tool="get_mass_properties", params={})] | 三个任务无依赖，可并行执行 |

## Implementation Notes

### Task Dependencies
- create_part: 无依赖
- create_sketch: 依赖 create_part
- create_rectangle/circle: 依赖 create_sketch
- extrude_boss/extrude_cut: 依赖 create_rectangle/circle
- modify_dimension/modify_feature: 无依赖
- analyze/export: 无依赖

### Error Handling
- 缺少必需参数: 抛出 ValueError
- 未知实体类型: 抛出 ValueError
- 未知动作类型: 抛出 ValueError
- 无效参数值: 抛出 ValueError（如负数、零尺寸）
