# 快速测试指南 - CreateSketch修复验证

## ⚡ 5分钟快速测试

### 步骤1: 打开SolidWorks
```
启动 SolidWorks 2026
```

### 步骤2: 创建零件文档
```
文件 → 新建 → 零件 → 确定
```

### 步骤3: 运行测试

**方法A - 直接运行（推荐）**:
```powershell
cd "D:\sw2026\代码\测试代码"
D:\app_install\python.exe test_createsketch_manual.py
```

**方法B - 使用Python**:
```powershell
# 打开命令提示符
cd "D:\sw2026\代码\测试代码"
D:\app_install\python.exe test_createsketch_manual.py
```

### 步骤4: 查看结果

#### ✅ 成功输出示例：
```
[SUCCESS] CreateSketch成功！

重大突破！

这证明：
  1. C# SWHelper可以工作
  2. 'Front Plane' 基准面名称是正确的
  3. SelectByID2 with ref callout可以工作
```

#### ❌ 失败输出示例：
```
[INFO] CreateSketch返回False

错误信息: CreateSketch失败，已尝试4种方法

分析：所有4种fallback方法都失败了
```

---

## 🔍 如果测试失败

### 可能原因1：没有活动文档
**错误**: "没有活动文档"
**解决**:
1. 在SolidWorks中：文件 → 新建 → 零件
2. 确保零件窗口是活动状态
3. 重新运行测试

### 可能原因2：基准面名称问题
**错误**: 提到"Front Plane"但选择失败
**解决**:
1. 在SolidWorks FeatureManager设计树中查看基准面名称
2. 可能需要尝试：
   - "Front Plane" (英文)
   - "Plane1" (数字编号)
   - "基准面1" (中文编号)

### 可能原因3：其他API问题
**错误**: 其他错误信息
**解决**:
1. 截图错误信息
2. 检查SolidWorks版本是否为2026
3. 尝试重启SolidWorks

---

## 📋 测试结果报告

请将测试结果反馈：

**成功** ✅：
```
测试时间：____
测试人员：____
SolidWorks版本：____
测试结果：[SUCCESS] CreateSketch成功
下一步：实现M5设计器
```

**失败** ❌：
```
测试时间：____
测试人员：____
SolidWorks版本：____
错误信息：____
（请截图）
```

---

## 🎯 关键修复点

**修复内容**:
- 基准面名称: "前视基准面" → "Front Plane"
- 编译时间: 2026-04-14 20:59
- DLL文件: `bin\Release\SWHelper.Robust.dll`

**技术细节**:
- 使用英文API标识符
- ref callout参数处理
- 4种fallback方法

---

## 📞 下一步

**如果成功**:
- 开始实现M5螺栓和螺母设计器
- 预计时间: 12-14小时

**如果失败**:
- 收集详细错误信息
- 查看SolidWorks API文档
- 尝试其他解决方案

---

**准备好了吗？请开始测试！**
