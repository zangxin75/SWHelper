# 功能: 意图理解模块

**所属模块**: 第一阶段 - 基础Agent框架
**依赖**: Claude API (可选), 知识库
**类型**: 集成测试 (需mock Claude API)
**文件**: `代码/Python脚本/intent_understanding.py`

## 需求表

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| I-01 | 识别创建动作 | "创建一个方块" | action=CREATE, object=PART | 正常场景 |
| I-02 | 识别修改动作 | "修改零件尺寸" | action=MODIFY, object=PART | 正常场景 |
| I-03 | 识别分析动作 | "分析质量属性" | action=ANALYZE | 正常场景 |
| I-04 | 识别导出动作 | "导出STEP格式" | action=EXPORT | 正常场景 |
| I-05 | 提取尺寸参数 | "100x100x50mm的方块" | dimensions=[100,100,50] | 正常场景 |
| I-06 | 提取材料 | "铝合金方块" | material="铝合金_6061" | 正常场景 |
| I-07 | 空输入处理 | "" | confidence=0, error="Empty input" | 异常场景 |
| I-08 | 模糊输入 | "做东西" | action=CREATE, confidence<0.5 | 边界场景 |
| I-09 | 复杂描述 | "创建带M10安装孔的轴承座" | 正确识别所有关键词 | 正常场景 |
| I-10 | Claude模式-简单创建 | "创建方块"(use_claude=True) | action=CREATE, confidence>0.9 | Claude增强 |
| I-11 | 本地模式-Claude失败降级 | "创建方块"(claude_error) | 本地模式成功返回 | 降级场景 |
