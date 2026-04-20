# V5 测试指南

**新版本**: V5 (21:13:53编译)
**关键修复**: 延迟SketchManager初始化

---

## ⚡ 2分钟测试

### 准备工作
1. SolidWorks 2026正在运行
2. **已创建新零件文档**（文件 → 新建 → 零件）

### 运行测试
```powershell
cd "D:\sw2026\代码\测试代码"
D:\app_install\python.exe test_createsketch_manual.py
```

---

## 📊 结果解读

### ✅ 成功
```
[SUCCESS] CreateSketch成功！
```
→ **太好了！** V5的延迟初始化策略有效！

### ❌ 情况1：连接失败
```
[ERROR] SWHelper连接失败
```
→ RefreshModel仍然有问题，需要进一步调查

### ❌ 情况2：SketchManager初始化失败
```
错误信息: 无法获取SketchManager: DISP_E_BADINDEX
```
→ 即使延迟初始化也无法访问，可能是文档状态问题

### ❌ 情况3：基准面选择失败
```
DIAGNOSTICS:
- SketchManager延迟初始化成功
- 方案1: SelectByID2返回False
```
→ SketchManager可以访问，但基准面名称或参数有问题

---

## 🔍 V5相比V4的关键改进

**V4问题**：
```
连接时就失败：DISP_E_BADINDEX
→ 所有后续操作都无法执行
```

**V5改进**：
```
连接阶段：不访问SketchManager
CreateSketch阶段：才尝试访问
→ 如果失败，至少可以看到清晰的错误信息
```

---

## 🎯 如果成功意味着什么

✅ CreateSketch功能可用
✅ C#与SolidWorks 2026兼容
✅ 延迟初始化策略验证成功
✅ 可以开始实现M5螺栓和螺母设计器（12-14小时）

---

## 📝 测试后请报告

**测试结果**：成功 / 失败

**如果失败**，请提供：
1. 完整的错误信息
2. 在哪个阶段失败（连接/CreateSketch）
3. SolidWorks文档状态

---

**准备好测试V5了吗？请确保在SolidWorks中打开了零件文档！** 🚀
