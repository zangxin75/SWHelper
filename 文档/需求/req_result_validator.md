# Result Validator Module Requirements

## 模块概述
验证设计结果是否符合设计意图和设计规则，生成验证报告和改进建议。

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| V-01 | 验证成功的任务执行 | results = [{"feature": "Extrude", "status": "success"}], intent = {"type": "box", "size": [100, 100, 50]} | ValidationReport(success=True, passed=1, failed=0, warnings=0) | 所有验证通过 |
| V-02 | 检测失败的任务 | results = [{"feature": "Extrude", "status": "failed", "error": "Sketch invalid"}], intent = {"type": "box"} | ValidationReport(success=False, passed=0, failed=1, warnings=0, errors=["Task failed: Sketch invalid"]) | 检测到任务失败 |
| V-03 | 检查壁厚设计规则 | results = [{"feature": "Shell", "thickness": 2}], intent = {"min_thickness": 3}, knowledge_base = {"min_thickness": 3} | ValidationReport(success=False, warnings=["壁厚 2mm 小于最小值 3mm"]) | 壁厚不符合规则 |
| V-04 | 检查拔模角度设计规则 | results = [{"feature": "Draft", "angle": 0.5}], intent = {"draft_angle": 1}, knowledge_base = {"min_draft": 1} | ValidationReport(success=False, warnings=["拔模角度 0.5° 小于最小值 1°"]) | 拔模角度不符合 |
| V-05 | 检查圆角设计规则 | results = [{"feature": "Fillet", "radius": 0.5}], intent = {}, knowledge_base = {"min_fillet": 1} | ValidationReport(success=False, warnings=["圆角半径 0.5mm 小于最小值 1mm"]) | 圆角半径不符合 |
| V-06 | 计算质量指标 | results = [{"metrics": {"mass": 1500, "volume": 500000}}], intent = {} | ValidationReport(success=True, metrics={"mass": 1500, "volume": 500000}) | 成功提取质量体积 |
| V-07 | 生成验证建议 | results = [{"feature": "Extrude", "depth": 5}], intent = {"min_depth": 10}, knowledge_base = {} | ValidationReport(success=False, suggestions=["建议增加拉伸深度至至少 10mm"]) | 生成改进建议 |
| V-08 | 验证原始意图参数 | results = [{"feature": "Extrude", "depth": 50}], intent = {"depth": 100} | ValidationReport(success=False, errors=["拉伸深度 50mm 不符合设计意图 100mm"]) | 参数不匹配意图 |
| V-09 | 处理空结果 | results = [], intent = {"type": "box"} | ValidationReport(success=False, errors=["没有可验证的结果"]) | 空结果处理 |
| V-10 | 处理缺失的指标数据 | results = [{"feature": "Extrude", "status": "success"}], intent = {} | ValidationReport(success=True, metrics={"mass": 0, "volume": 0}, warnings=["无法获取质量指标"]) | 缺失指标时返回默认值 |
| V-11 | 验证多项设计规则 | results = [{"thickness": 2, "draft": 0.5, "fillet": 0.5}], intent = {}, knowledge_base = {"min_thickness": 3, "min_draft": 1, "min_fillet": 1} | ValidationReport(success=False, warnings=["壁厚 2mm 小于最小值 3mm", "拔模角度 0.5° 小于最小值 1°", "圆角半径 0.5mm 小于最小值 1mm"]) | 多项规则同时检查 |
| V-12 | 验证通过所有规则 | results = [{"thickness": 5, "draft": 3, "fillet": 2, "metrics": {"mass": 1000, "volume": 400000}}], intent = {"thickness": 5}, knowledge_base = {"min_thickness": 3} | ValidationReport(success=True, passed=3, metrics={"mass": 1000, "volume": 400000}) | 所有验证通过 |

## 设计规则定义

| 规则名称 | 最小值 | 单位 | 说明 |
|---------|--------|------|------|
| min_thickness | 3 | mm | 最小壁厚 |
| min_draft | 1 | degree | 最小拔模角度 |
| min_fillet | 1 | mm | 最小圆角半径 |

## 指标定义

| 指标名称 | 单位 | 说明 |
|---------|------|------|
| mass | g | 质量（克） |
| volume | mm³ | 体积（立方毫米） |

## 验证报告结构

```python
@dataclass
class ValidationReport:
    success: bool              # 整体验证是否通过
    passed: int                # 通过的验证项数量
    failed: int                # 失败的验证项数量
    warnings: List[str]        # 警告列表（不符合设计规则）
    errors: List[str]          # 错误列表（任务失败、参数不匹配）
    suggestions: List[str]     # 改进建议
    metrics: Dict[str, float]  # 设计指标（质量、体积等）
```
