# Phase 2 需求表：修复问题 + 增强功能

**创建日期**: 2026-04-13
**需求编号**: FIX-01 到 FIX-06, ENH-01 到 ENH-10
**对应实施**: Phase 2 - 修复Phase 1问题 + 增强现有模块

---

## Part C: 修复Phase 1的6个E2E测试失败

### 测试失败分析

| 测试编号 | 测试名称 | 预期行为 | 实际行为 | 根本原因 |
|---------|---------|---------|---------|---------|
| E2E-05 | test_e2e_error_handling with "!!###@" | success=False, error_type="IntentError" | success=True, error_type=None | 意图理解模块过度宽容，未正确处理无意义输入 |
| E2E-08 | test_e2e_complex_workflow | 支持3步连续操作（创建→倒角→分析） | 第二步"添加倒角"失败 | 任务分解模块不支持"在现有模型上添加特征" |
| E2E-09 | test_e2e_mass_properties_analysis | 创建+分析，返回质量信息 | 缺少质量分析结果 | 任务分解未正确处理"并分析质量"的复合指令 |
| E2E-13 | test_module_integration | 所有模块正确集成 | 意图理解返回FEATURE而非PART | 对象识别逻辑问题（"立方体"→FEATURE vs PART） |
| E2E-14 | test_knowledge_base_integration | 识别标准件"M10x20螺栓" | 未识别"螺栓"为标准件 | 知识库查询未正确匹配标准件 |
| E2E-16 | test_mixed_language | 处理中英文混合输入 | success但feedback中无"100" | 中英文混合的尺寸提取逻辑不完善 |

---

## FIX-01: 意图理解 - 拒绝非结构化输入

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| FIX-01-01 | 空字符串 | "" | success=False, error_type="IntentError", feedback包含"无法理解" | 空输入应立即失败 |
| FIX-01-02 | 纯特殊字符 | "!!###@" | success=False, error_type="IntentError", feedback包含"无法理解" | 无意义输入应失败 |
| FIX-01-03 | 纯标点符号 | "。。。？？？" | success=False, error_type="IntentError", feedback包含"无法理解" | 标点符号不应被理解为有效意图 |
| FIX-01-04 | 无关键词 | "asdfgh" | success=False, error_type="IntentError", feedback包含"无法理解" | 无关键词输入应失败 |
| FIX-01-05 | 极短输入 | "创" | success=False, error_type="IntentError", feedback包含"信息不足" | 单字输入信息不足 |
| FIX-01-06 | 正常创建指令（验证未误伤） | "创建方块" | success=True, action="CREATE", object="PART" | 确保正常输入不受影响 |

**验收标准**:
- 6个测试用例全部通过
- E2E-05测试通过
- 代码覆盖率保持≥90%

---

## FIX-02: 任务分解 - 支持在现有模型上添加特征

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| FIX-02-01 | 添加倒角（有现有模型） | "在顶部添加10mm倒角" | tasks包含"create_fillet", parameters={"size": 10} | 识别添加特征操作 |
| FIX-02-02 | 添加圆角（有现有模型） | "在边缘添加5mm圆角" | tasks包含"create_fillet", parameters={"radius": 5} | 区分倒角和圆角 |
| FIX-02-03 | 添加孔（有现有模型） | "在中心添加直径10mm的孔" | tasks包含"create_extrude_cut", parameters={"diameter": 10} | 识别切除特征 |
| FIX-02-04 | 添加阵列（有现有模型） | "创建线性阵列，间距20mm，数量5" | tasks包含"create_linear_pattern" | 识别阵列特征 |
| FIX-02-05 | 多特征添加 | "添加10mm倒角和5mm圆角" | tasks包含2个工具调用 | 支持一次添加多个特征 |
| FIX-02-06 | 无现有模型时添加特征 | "在立方体上添加倒角"（无前置模型） | success=False, error_type="ContextError" | 应拒绝无上下文的特征添加 |

**验收标准**:
- 6个测试用例全部通过
- E2E-08测试通过（复杂工作流：创建→倒角→分析）
- 代码覆盖率保持≥90%

---

## FIX-03: 任务分解 - 支持复合指令（创建+分析）

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| FIX-03-01 | 创建并分析质量 | "创建方块并分析质量" | tasks包含create_part和calculate_mass | 识别"并"连接的复合操作 |
| FIX-03-02 | 创建并导出 | "创建圆柱并导出STEP" | tasks包含create_part和export_step | 识别导出指令 |
| FIX-03-03 | 创建并设置材料 | "创建零件，材料为铝合金" | tasks包含create_part和assign_material | 识别材料设置 |
| FIX-03-04 | 创建、分析、导出（三重） | "创建方块，分析质量，导出PDF" | tasks包含3个工具调用 | 支持多个复合操作 |
| FIX-03-05 | 无连接词的复合操作 | "创建方块分析质量" | tasks包含create_part和calculate_mass | 支持隐式连接 |
| FIX-03-06 | 单一操作（验证未误伤） | "创建方块" | tasks仅包含create_part | 确保单一操作不受影响 |

**验收标准**:
- 6个测试用例全部通过
- E2E-09测试通过（质量属性分析）
- 代码覆盖率保持≥90%

---

## FIX-04: 意图理解 - 对象识别修正

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| FIX-04-01 | "立方体"应识别为PART | "创建立方体" | object="PART", not "FEATURE" | 立方体是完整零件，不是特征 |
| FIX-04-02 | "长方体"应识别为PART | "创建长方体" | object="PART", not "FEATURE" | 长方体是完整零件 |
| FIX-04-03 | "圆柱体"应识别为PART | "创建圆柱体" | object="PART", not "FEATURE" | 圆柱体是完整零件 |
| FIX-04-04 | "倒角"应识别为FEATURE | "添加倒角" | object="FEATURE" | 倒角是特征，需要现有模型 |
| FIX-04-05 | "孔"应识别为FEATURE | "打孔" | object="FEATURE" | 孔是特征 |
| FIX-04-06 | "装配体"应识别为ASSEMBLY | "创建装配体" | object="ASSEMBLY" | 装配体类型识别 |

**验收标准**:
- 6个测试用例全部通过
- E2E-13测试通过（模块集成测试）
- 代码覆盖率保持≥90%

---

## FIX-05: 知识库 - 标准件查询优化

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| FIX-05-01 | 标准螺栓查询 | "M10x20螺栓" | 返回标准件信息，feedback包含"螺栓" | 识别标准件格式 |
| FIX-05-02 | 标准螺母查询 | "M8螺母" | 返回标准件信息，feedback包含"螺母" | 螺母标准件 |
| FIX-05-03 | 标准轴承查询 | "6200轴承" | 返回标准件信息，feedback包含"轴承" | 轴承标准件 |
| FIX-05-04 | 模糊匹配 | "M10的螺栓" | 返回标准件信息（忽略x20） | 支持不完整规格 |
| FIX-05-05 | 不存在的标准件 | "M1000螺栓" | success=False, error="StandardComponentNotFound" | 优雅处理不存在 |
| FIX-05-06 | 非标准件 | "创建一个特殊的连接件" | 不触发标准件查询 | 避免误判 |

**验收标准**:
- 6个测试用例全部通过
- E2E-14测试通过（知识库集成测试）
- 代码覆盖率保持≥90%

---

## FIX-06: 意图理解 - 中英文混合尺寸提取

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| FIX-06-01 | 中英文混合（英文数字） | "Create a 100x100x50mm 的 长方体" | dimensions=[100, 100, 50], feedback包含"100" | 提取英文数字 |
| FIX-06-02 | 中英文混合（中文数字） | "Create 一个 100x100x50mm 的方块" | dimensions=[100, 100, 50] | 中文连接词不影响 |
| FIX-06-03 | 全英文 | "Create a 100x100x50mm cube" | dimensions=[100, 100, 50] | 纯英文输入 |
| FIX-06-04 | 全中文（mm单位） | "创建100x100x50mm的长方体" | dimensions=[100, 100, 50] | 中文输入 |
| FIX-06-05 | 全中文（汉字单位） | "创建100x100x50毫米的长方体" | dimensions=[100, 100, 50] | 汉字单位 |
| FIX-06-06 | 单位混合 | "100mm x 100厘米 x 50m 的方块" | dimensions=[100, 1000, 50000] | 正确单位换算 |

**验收标准**:
- 6个测试用例全部通过
- E2E-16测试通过（中英文混合测试）
- 代码覆盖率保持≥90%

---

## Part A: 增强现有模块功能

### ENH-01: 意图理解 - 装配体设计支持

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-01-01 | 创建装配体 | "创建一个装配体，包含3个零件" | object="ASSEMBLY", parameters={"component_count": 3} | 识别装配体创建 |
| ENH-01-02 | 插入配合 | "添加同轴配合" | action="MODIFY", object="ASSEMBLY", parameters={"mate_type": "coaxial"} | 识别配合操作 |
| ENH-01-03 | 干涉检查 | "检查装配体干涉" | action="ANALYZE", object="ASSEMBLY", parameters={"check_type": "interference"} | 识别分析指令 |
| ENH-01-04 | 爆炸视图 | "创建爆炸视图" | action="MODIFY", object="ASSEMBLY", parameters={"view_type": "exploded"} | 识别爆炸视图 |
| ENH-01-05 | 装配体材料 | "装配体材料为铝合金" | parameters={"material": "铝合金_6061"} | 装配体材料设置 |
| ENH-01-06 | 子装配体 | "创建子装配体" | object="ASSEMBLY", parameters={"is_subassembly": True} | 子装配体识别 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥85%
- 支持基础装配体操作

---

### ENH-02: 意图理解 - 工程图创建支持

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-02-01 | 创建工程图 | "创建工程图，3个视图" | object="DRAWING", parameters={"view_count": 3} | 识别工程图创建 |
| ENH-02-02 | 添加尺寸 | "添加所有尺寸" | action="MODIFY", object="DRAWING", parameters={"annotation": "dimensions"} | 识别尺寸标注 |
| ENH-02-03 | 添加注释 | "添加技术要求注释" | action="MODIFY", object="DRAWING", parameters={"annotation": "note"} | 识别注释 |
| ENH-02-04 | 导出PDF | "导出工程图为PDF" | action="EXPORT", object="DRAWING", parameters={"format": "pdf"} | 识别PDF导出 |
| ENH-02-05 | 图纸格式 | "使用A3图纸" | parameters={"sheet_format": "A3"} | 识别图纸格式 |
| ENH-02-06 | 比例设置 | "比例1:2" | parameters={"scale": "1:2"} | 识别比例 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥85%
- 支持基础工程图操作

---

### ENH-03: 意图理解 - 钣金设计支持

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-03-01 | 创建钣金零件 | "创建厚度2mm的钣金" | object="PART", parameters={"sheet_metal": True, "thickness": 2} | 识别钣金创建 |
| ENH-03-02 | 添加折弯 | "添加90度折弯" | tasks包含"create_bend", parameters={"angle": 90} | 识别折弯特征 |
| ENH-03-03 | 展开钣金 | "展开钣金" | action="ANALYZE", parameters={"operation": "flatten"} | 识别展开操作 |
| ENH-03-04 | 添加凹槽 | "创建凹槽特征" | tasks包含"create_hem" | 识别凹槽 |
| ENH-03-05 | 钣金切口 | "创建切口" | tasks包含"create_louver" | 识别切口 |
| ENH-03-06 | 钣金材料 | "钣金材料为不锈钢" | parameters={"material": "不锈钢_304"} | 钣金材料识别 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥85%
- 支持基础钣金操作

---

### ENH-04: 意图理解 - 复杂特征识别

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-04-01 | 扫描特征 | "创建扫描特征，路径是圆，截面是方形" | tasks包含"create_sweep", parameters={"path": "circle", "profile": "square"} | 识别扫描 |
| ENH-04-02 | 放样特征 | "创建放样，从圆到方" | tasks包含"create_loft" | 识别放样 |
| ENH-04-03 | 螺旋线 | "创建螺旋线特征" | tasks包含"create_helix" | 识别螺旋线 |
| ENH-04-04 | 拔模角度 | "添加3度拔模角度" | tasks包含"create_draft", parameters={"angle": 3} | 识别拔模 |
| ENH-04-05 | 加强筋 | "创建加强筋" | tasks包含"create_rib" | 识别加强筋 |
| ENH-04-06 | 弯曲特征 | "创建弯曲特征" | tasks包含"create_bend" | 识别弯曲 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥85%
- 支持复杂特征识别

---

### ENH-05: Claude API集成 - 增强NLU

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-05-01 | Claude理解复杂指令 | "设计一个轴承座，底座200x150x20mm，支撑高度100mm" | Claude增强模式返回更精确的意图 | Claude API调用成功 |
| ENH-05-02 | Claude降级到本地 | Claude API失败 | 自动降级到本地模式，success=True | 优雅降级 |
| ENH-05-03 | Claude参数提取 | "创建一个轴承座，顶部有直径50mm的孔" | 提取diameter=50 | Claude精确提取参数 |
| ENH-05-04 | Claude设计建议 | "这个支架太重了" | 返回优化建议 | Claude提供设计建议 |
| ENH-05-05 | Claude错误处理 | 输入包含恶意内容 | success=False, error_type="SafetyError" | Claude安全过滤 |
| ENH-05-06 | 本地模式验证 | 无API密钥时 | 使用本地模式，success=True | 无API也能工作 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥85%
- Claude集成稳定可用

---

### ENH-06: 结果验证 - 更严格的设计规则

| 编号 | 场景描述 | 输入（设计结果） | 预期输出 | 备注 |
|------|---------|----------------|---------|------|
| ENH-06-01 | 壁厚检查 | dimensions=[1, 1, 1]（mm） | validation.passed=False, issues包含"壁厚过小" | 检查最小壁厚 |
| ENH-06-02 | 拔模角度检查 | draft_angle=0.5 | validation.warnings包含"拔模角度过小" | 检查拔模角度 |
| ENH-06-03 | 圆角半径检查 | fillet_radius=2, wall_thickness=50 | validation.passed=False, issues包含"圆角半径过小" | 检查圆角半径≥壁厚25% |
| ENH-06-04 | 孔径检查 | hole_diameter=2.5 | validation.warnings包含"非标准孔径" | 检查标准孔径 |
| ENH-06-05 | 长宽比检查 | length=100, width=5, thickness=10 | validation.warnings包含"长宽比过大" | 检查长宽比 |
| ENH-06-06 | 材料适用性 | material="铝合金_6061", application="高温" | validation.warnings包含"材料不适合高温" | 检查材料适用性 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥85%
- 设计规则检查完善

---

### ENH-07: 工具调用 - 真实MCP集成

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-07-01 | 真实模式调用 | use_real_sw=True, call_tool("create_part") | 成功调用真实MCP工具 | 真实SW环境 |
| ENH-07-02 | 超时处理 | call_tool("slow_operation"), timeout=5 | 5秒后超时，自动重试 | 超时重试 |
| ENH-07-03 | 错误重试 | call_tool("unstable_tool") | 失败后自动重试最多3次 | 指数退避 |
| ENH-07-04 | Mock/Real切换 | use_real_sw=False → True | 无缝切换，不影响功能 | 模式切换 |
| ENH-07-05 | 工具不存在 | call_tool("non_existent_tool") | ToolResult.success=False, error="ToolNotFound" | 优雅处理 |
| ENH-07-06 | 参数验证 | call_tool("create_part", invalid_param) | ToolResult.success=False, error="InvalidParameter" | 参数校验 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥80%
- 真实MCP集成稳定

---

### ENH-08: 任务执行 - 并行优化

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-08-01 | 并行执行无依赖任务 | tasks=[task1, task2, task3], 无依赖 | 执行时间 < 串行总时间的60% | 并行加速 |
| ENH-08-02 | 串行执行有依赖任务 | tasks=[task1→task2→task3] | 按依赖顺序执行 | 依赖正确 |
| ENH-08-03 | 混合依赖图 | tasks=[A→C, B→C, D], A/B无依赖 | A/B并行，然后C，最后D | 正确拓扑排序 |
| ENH-08-04 | 循环依赖检测 | tasks=[A→B→A] | 执行失败，error="CircularDependency" | 循环检测 |
| ENH-08-05 | 部分失败回滚 | tasks=[A(成功), B(失败), C(未执行)] | A的结果被回滚或标记 | 失败回滚 |
| ENH-08-06 | 执行统计 | 任意tasks | ExecutionResult包含详细时间统计 | 性能监控 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥90%
- 并行执行性能提升≥40%

---

### ENH-09: Agent Coordinator - 多轮对话支持

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-09-01 | 两步创建 | 第1步："创建方块", 第2步："添加倒角" | 两步都成功，保留上下文 | 上下文记忆 |
| ENH-09-02 | 修改设计 | 第1步："创建立方体", 第2步："修改为圆柱体" | 第2步替换第1步的结果 | 设计修改 |
| ENH-09-03 | 查看历史 | "显示我刚才创建的零件" | 返回之前创建的零件信息 | 历史查询 |
| ENH-09-04 | 撤销操作 | "撤销上一步操作" | 恢复到之前的状态 | 撤销功能 |
| ENH-09-05 | 保存会话 | "保存当前设计" | 保存到文件 | 会话持久化 |
| ENH-09-06 | 清空上下文 | "清空当前设计" | 清除所有历史记录 | 重新开始 |

**验收标准**:
- 6个测试用例全部通过
- 代码覆盖率≥80%
- 多轮对话流畅

---

### ENH-10: 性能优化 - 响应时间提升

| 编号 | 场景描述 | 输入 | 预期输出 | 备注 |
|------|---------|------|---------|------|
| ENH-10-01 | 简单请求响应时间 | "创建方块" | total_time < 0.5秒（mock模式） | 快速响应 |
| ENH-10-02 | 复杂请求响应时间 | "创建装配体并分析" | total_time < 2.0秒（mock模式） | 合理时间 |
| ENH-10-03 | Claude API调用 | Claude增强模式 | intent_time < 3.0秒（含网络） | Claude超时 |
| ENH-10-04 | 缓存机制 | 重复相同请求 | 第2次时间 < 第1次时间的50% | 缓存生效 |
| ENH-10-05 | 并发请求 | 3个并发请求 | 总时间 < 单个请求时间的2倍 | 并行效率 |
| ENH-10-06 | 内存使用 | 处理100个任务 | 内存增长 < 100MB | 内存控制 |

**验收标准**:
- 6个测试用例全部通过
- 性能达标
- 内存无泄漏

---

## 实施优先级

### P0 (必须修复) - 阻塞E2E测试
- FIX-01: 意图理解 - 拒绝非结构化输入
- FIX-02: 任务分解 - 支持在现有模型上添加特征
- FIX-03: 任务分解 - 支持复合指令
- FIX-04: 意图理解 - 对象识别修正
- FIX-05: 知识库 - 标准件查询优化
- FIX-06: 意图理解 - 中英文混合尺寸提取

### P1 (高价值增强)
- ENH-01: 装配体设计支持
- ENH-02: 工程图创建支持
- ENH-05: Claude API增强NLU
- ENH-07: 真实MCP集成

### P2 (中等价值)
- ENH-03: 钣金设计支持
- ENH-04: 复杂特征识别
- ENH-06: 更严格的设计规则
- ENH-08: 任务执行并行优化

### P3 (锦上添花)
- ENH-09: 多轮对话支持
- ENH-10: 性能优化

---

## 验收总标准

**Part C (修复问题)**:
- ✅ 6个E2E测试全部通过
- ✅ 代码覆盖率保持≥85%
- ✅ 无回归问题（Phase 1的121个测试依然通过）

**Part A (增强功能)**:
- ✅ 至少完成P0 + P1优先级的需求
- ✅ 新增代码覆盖率≥80%
- ✅ 所有新功能有对应的测试用例

**Phase 2整体目标**:
- E2E测试通过率: 从62.5% (10/16) 提升到 ≥90%
- 总测试数: 从141个提升到 ≥200个
- 代码覆盖率: 从84%提升到 ≥88%

---

**文档版本**: 1.0
**状态**: ✅ 需求表已完成，待转换为测试用例
