using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using System.Reflection;

namespace SWHelper
{
    /// <summary>
    /// SWHelper 高可靠性版本
    /// 核心设计原则：
    /// 1. 连接稳定性 - 多重重试和备用方案
    /// 2. API调用健壮性 - 参数验证和错误处理
    /// 3. 状态管理 - 实时检测和自动恢复
    /// 4. 版本管理 - 清晰的版本和兼容性
    /// </summary>

    [ComVisible(true)]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelperRobust
    {
        // 核心连接方法
        string GetVersion();
        string GetSystemStatus();
        bool ConnectToSW();
        bool DisconnectFromSW();
        bool IsSWConnected();

        // 文档创建（高可靠性）
        bool CreatePart();
        bool CreatePartSafe();
        bool HasActiveDocument();

        // 草图操作（带状态检查）
        bool CreateSketch();
        bool CloseSketch();
        bool InSketchMode();

        // 绘图操作（带参数验证）
        bool DrawRectangle(double x1, double y1, double x2, double y2);
        bool DrawCircle(double centerX, double centerY, double radius);
        bool DrawLine(double x1, double y1, double x2, double y2);

        // 特征操作（带前置检查）
        bool CreateExtrusion(double depth);
        bool CreateCut(double depth);
        bool CreateChamfer(double distance, double angle);

        // 关键新方法
        bool CreateInternalThread(double diameter, double pitch, double length);

        // 状态和错误
        string GetLastError();
        string GetLastOperation();
        bool GetConnectionHealth();
    }

    [ComVisible(true)]
    [ProgId("SWHelper.Robust")]
    [ClassInterface(ClassInterfaceType.None)]
    [Guid("E5F5E5A0-5D5D-5D5D-5D5D-5D5D5D5D5D5D")]
    public class SWHelperRobust : ISWHelperRobust
    {
        // 版本信息
        private const string VERSION = "2.0-Robust";
        private const string BUILD_DATE = "2026.04.14";

        // SolidWorks对象（使用弱引用避免内存泄漏）
        private SldWorks swApp;
        private dynamic model;
        private dynamic sketchMgr;
        private dynamic featureMgr;

        // 状态管理
        private bool isConnected = false;
        private bool inSketch = false;
        private string lastError = "";
        private string lastOperation = "";
        private int connectionAttempts = 0;
        private const int MAX_CONNECTION_ATTEMPTS = 3;

        // 重试配置
        private const int RETRY_COUNT = 3;
        private const int RETRY_DELAY_MS = 1000;

        public string GetVersion()
        {
            return "SWHelper v" + VERSION + " (Robust Architecture)";
        }

        public string GetSystemStatus()
        {
            System.Text.StringBuilder status = new System.Text.StringBuilder();
            status.AppendLine("=== SWHelper System Status ===");
            status.AppendLine("Version: " + VERSION);
            status.AppendLine("Build: " + BUILD_DATE);
            status.AppendLine("Connected: " + (isConnected ? "YES" : "NO"));
            status.AppendLine("In Sketch: " + (inSketch ? "YES" : "NO"));
            status.AppendLine("Has Document: " + (model != null ? "YES" : "NO"));
            status.AppendLine("Connection Health: " + (GetConnectionHealth() ? "GOOD" : "POOR"));
            status.AppendLine("Last Operation: " + lastOperation);
            if (!string.IsNullOrEmpty(lastError))
            {
                status.AppendLine("Last Error: " + lastError);
            }
            return status.ToString();
        }

        /// <summary>
        /// 高可靠性连接方法 - 带重试和备用方案
        /// </summary>
        public bool ConnectToSW()
        {
            lastOperation = "ConnectToSW";
            connectionAttempts++;

            try
            {
                // 方案1: 尝试连接现有实例
                for (int i = 0; i < RETRY_COUNT; i++)
                {
                    try
                    {
                        swApp = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
                        if (swApp != null)
                        {
                            isConnected = true;
                            lastError = "";
                            LogSuccess("Connected to existing SolidWorks instance");

                            // 重要：更新model对象
                            RefreshModel();

                            return true;
                        }
                    }
                    catch (COMException)
                    {
                        if (i < RETRY_COUNT - 1)
                        {
                            System.Threading.Thread.Sleep(RETRY_DELAY_MS);
                        }
                    }
                }

                // 方案2: 创建新实例
                for (int i = 0; i < RETRY_COUNT; i++)
                {
                    try
                    {
                        swApp = new SldWorks();
                        if (swApp != null)
                        {
                            swApp.Visible = true;
                            isConnected = true;
                            lastError = "";
                            LogSuccess("Created new SolidWorks instance");

                            // 重要：更新model对象
                            RefreshModel();

                            return true;
                        }
                    }
                    catch (Exception ex)
                    {
                        LogWarning("Failed to create SolidWorks instance: " + ex.Message);
                        if (i < RETRY_COUNT - 1)
                        {
                            System.Threading.Thread.Sleep(RETRY_DELAY_MS);
                        }
                    }
                }

                lastError = "无法连接SolidWorks（已尝试" + (RETRY_COUNT * 2) + "次）";
                return false;
            }
            catch (Exception ex)
            {
                lastError = "连接异常: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 刷新model对象 - V5修复：延迟初始化Manager避免DISP_E_BADINDEX
        /// </summary>
        public bool RefreshModel()
        {
            lastOperation = "RefreshModel";

            try
            {
                if (swApp != null)
                {
                    // 释放旧的model对象
                    if (model != null)
                    {
                        try
                        {
                            Marshal.ReleaseComObject(model);
                        }
                        catch { }
                        model = null;
                    }

                    // 释放旧的管理器
                    if (sketchMgr != null)
                    {
                        try
                        {
                            Marshal.ReleaseComObject(sketchMgr);
                        }
                        catch { }
                        sketchMgr = null;
                    }

                    if (featureMgr != null)
                    {
                        try
                        {
                            Marshal.ReleaseComObject(featureMgr);
                        }
                        catch { }
                        featureMgr = null;
                    }

                    // 获取当前活动文档
                    model = swApp.ActiveDoc;

                    // V5关键修复：不在这里访问任何Manager，延迟到需要时
                    if (model != null)
                    {
                        LogSuccess("Model对象已获取（Manager延迟初始化）");
                        return true;
                    }
                    else
                    {
                        LogWarning("No active document to refresh");
                        return false;
                    }
                }
                return false;
            }
            catch (Exception ex)
            {
                lastError = "刷新模型失败: " + ex.Message;
                // 确保model被设置为null以避免后续问题
                model = null;
                sketchMgr = null;
                featureMgr = null;
                return false;
            }
        }

        /// <summary>
        /// 断开连接并清理资源
        /// </summary>
        /// <summary>
        /// 获取当前活动文档
        /// 用于用户手动创建零件后，让COM组件获取文档对象
        /// </summary>
        public bool GetActiveDocument()
        {
            lastOperation = "GetActiveDocument";

            try
            {
                if (!ValidateConnection())
                {
                    return false;
                }

                // 获取当前活动文档
                model = swApp.IActiveDoc;

                if (model == null)
                {
                    lastError = "没有活动文档";
                    LogWarning("GetActiveDocument: 无活动文档");
                    return false;
                }

                // 初始化管理器
                InitializeManagers();

                LogSuccess("获取活动文档成功: " + model.GetTitle());
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "获取活动文档错误: " + ex.Message;
                LogError("GetActiveDocument 失败: " + ex.Message);
                return false;
            }
        }

        public bool DisconnectFromSW()
        {
            lastOperation = "DisconnectFromSW";

            try
            {
                // 清理COM对象
                if (sketchMgr != null)
                {
                    Marshal.ReleaseComObject(sketchMgr);
                    sketchMgr = null;
                }

                if (featureMgr != null)
                {
                    Marshal.ReleaseComObject(featureMgr);
                    featureMgr = null;
                }

                if (model != null)
                {
                    Marshal.ReleaseComObject(model);
                    model = null;
                }

                // 注意：不释放swApp，因为可能还有其他应用在使用
                isConnected = false;
                inSketch = false;
                lastError = "";
                LogSuccess("Disconnected and cleaned up resources");
                return true;
            }
            catch (Exception ex)
            {
                lastError = "断开连接错误: " + ex.Message;
                return false;
            }
        }

        public bool IsSWConnected()
        {
            if (!isConnected || swApp == null)
            {
                return false;
            }

            try
            {
                // 尝试访问SolidWorks属性来验证连接
                var visible = swApp.Visible;
                return true;
            }
            catch
            {
                isConnected = false;
                return false;
            }
        }

        /// <summary>
        /// 高可靠性文档创建 - 带模板检测和备用方案
        /// </summary>
        public bool CreatePart()
        {
            lastOperation = "CreatePart";

            if (!ValidateConnection())
            {
                return false;
            }

            try
            {
                // V6.1修复：使用完整的模板路径
                // Python 测试证明所有参数组合都有效，问题在于返回值处理

                string templatePath = @"C:\ProgramData\SolidWorks\SolidWorks 2026\templates\gb_part.prtdot";

                if (!System.IO.File.Exists(templatePath))
                {
                    lastError = "模板文件不存在: " + templatePath;
                    LogError("模板文件不存在");
                    return false;
                }

                LogWarning("V6.1修复: 使用模板路径 = " + templatePath);

                // 使用最简单的参数组合（Python 测试证明有效）
                object result = swApp.NewDocument(templatePath, 0, 0.0, 0.0);

                LogWarning("V6.3: NewDocument 返回成功");

                // V6.3关键修复：逐步诊断每个操作
                try
                {
                    // 步骤1: dynamic 转换
                    LogWarning("V6.3: 步骤1 - 尝试 dynamic 转换");
                    dynamic doc = result;
                    LogWarning("V6.3: 步骤1 - dynamic 转换成功");

                    // 步骤2: ModelDoc2 转换
                    LogWarning("V6.3: 步骤2 - 尝试 ModelDoc2 转换");
                    model = (ModelDoc2)doc;
                    LogWarning("V6.3: 步骤2 - ModelDoc2 转换成功");

                    // 步骤3: 获取标题（这可能导致 DISP_E_BADINDEX）
                    LogWarning("V6.3: 步骤3 - 尝试获取标题");
                    string title = null;
                    try
                    {
                        title = model.GetTitle();
                        LogWarning("V6.3: 步骤3 - 获取标题成功: " + (title ?? "(null)"));
                    }
                    catch (Exception titleEx)
                    {
                        LogWarning("V6.3: 步骤3 - GetTitle 失败: " + titleEx.Message);
                        // 继续执行，标题获取失败不代表失败
                    }

                    // 步骤4: 初始化管理器（这可能导致 DISP_E_BADINDEX）
                    LogWarning("V6.3: 步骤4 - 尝试 InitializeManagers");
                    try
                    {
                        InitializeManagers();
                        LogWarning("V6.3: 步骤4 - InitializeManagers 成功");
                    }
                    catch (Exception initEx)
                    {
                        LogWarning("V6.3: 步骤4 - InitializeManagers 失败: " + initEx.Message);
                        // 继续执行
                    }

                    LogSuccess("V6.3: 创建零件成功 (标题: " + (title ?? "(null)") + ")");
                    lastError = "";
                    return true;
                }
                catch (Exception ex)
                {
                    lastError = "V6.3: 异常 - " + ex.Message;
                    LogError("V6.3: " + ex.Message);
                    return false;
                }
            }
            catch (Exception ex)
            {
                lastError = "创建零件错误: " + ex.Message;
                LogError("CreatePart 异常: " + ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 安全模式创建零件 - 带更多验证
        /// </summary>
        public bool CreatePartSafe()
        {
            lastOperation = "CreatePartSafe";

            // 先验证连接
            if (!ValidateConnection())
            {
                return false;
            }

            // 检查是否已有文档
            if (HasActiveDocument())
            {
                LogWarning("已有活动文档，关闭旧文档");
                try
                {
                    swApp.CloseDoc(model.GetTitle());
                }
                catch { }
            }

            // 创建新零件
            return CreatePart();
        }

        public bool HasActiveDocument()
        {
            try
            {
                if (swApp == null) return false;
                var activeDoc = swApp.ActiveDoc;
                return activeDoc != null;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// 创建草图 - V8.9修复：添加延迟调用策略，解决零件初始化时序问题
        /// </summary>
        public bool CreateSketch()
        {
            lastOperation = "CreateSketch";

            LogWarning("V8.9: 开始 CreateSketch - 延迟调用策略");

            // 步骤1: 验证连接
            LogWarning("V8.2: 步骤1 - 验证连接");
            if (!ValidateConnection())
            {
                LogError("V8.2: 步骤1 - ValidateConnection 失败");
                return false;
            }
            LogWarning("V8.2: 步骤1 - 连接有效");

            // 步骤2: 检查 model 对象
            LogWarning("V8.2: 步骤2 - 检查 model 对象");
            if (model == null)
            {
                LogWarning("V8.2: 步骤2 - model 为 null，尝试获取 ActiveDoc");
                try
                {
                    model = swApp.ActiveDoc;
                    if (model != null)
                    {
                        LogWarning("V8.2: 步骤2 - ActiveDoc 获取成功");
                    }
                    else
                    {
                        LogError("V8.2: 步骤2 - ActiveDoc 返回 null");
                        lastError = "没有活动文档，请先在SolidWorks中创建零件";
                        return false;
                    }
                }
                catch (Exception ex)
                {
                    LogError("V8.2: 步骤2 - ActiveDoc 异常: " + ex.Message);
                    lastError = "获取活动文档失败: " + ex.Message;
                    return false;
                }
            }
            else
            {
                LogWarning("V8.2: 步骤2 - model 已存在");
            }

            // 步骤3: 初始化管理器
            LogWarning("V8.2: 步骤3 - 初始化管理器");
            try
            {
                InitializeManagers();
                LogWarning("V8.2: 步骤3 - InitializeManagers 成功");
            }
            catch (Exception ex)
            {
                LogWarning("V8.2: 步骤3 - InitializeManagers 失败: " + ex.Message);
                // 继续执行
            }

            // V8策略：使用dynamic实现晚绑定，避免类型不匹配
            LogWarning("V8策略：使用dynamic晚绑定");

            try
            {
                // V8.7修复: 延迟获取 SketchManager，在实际需要时才获取
                LogWarning("V8.7: 步骤1 - 创建 dynamicModel");
                dynamic dynamicModel = model;
                LogWarning("V8.7: 步骤1 - dynamicModel 创建成功");

                // 不在这里获取 SketchManager，而是在需要时才获取
                LogWarning("V8.7: 步骤2 - 跳过 SketchManager 预获取，将在需要时获取");

                // 声明 dynamicSketchMgr 变量（稍后在需要时赋值）
                dynamic dynamicSketchMgr = null;

                // V8.8修复: 移除错误的 null 检查
                // dynamicSketchMgr 在这里自然是 null，我们稍后会在需要时才获取
                LogWarning("V8.9: 进入基准面选择循环（带延迟策略）");

                // V8.9: 延迟策略 - 给零件时间完全初始化
                LogWarning("V8.9: 步骤0 - 等待2秒，让零件完全初始化");
                System.Threading.Thread.Sleep(2000);

                // 尝试多个基准面名称（使用dynamic调用）
                string[] planeNames = {
                    "Front Plane",
                    "前视基准面",
                    "Plane1",
                    "基准面1",
                    "Front"
                };

                bool sketchCreated = false;

                foreach (string planeName in planeNames)
                {
                    LogWarning("V8.9: 尝试基准面: '" + planeName + "'");

                    try
                    {
                        // V8.1: 逐步诊断每个操作
                        bool selected = false;

                        // V8.9修复: 每次选择前再延迟500ms
                        LogWarning("V8.9: 步骤1 - 延迟500ms");
                        System.Threading.Thread.Sleep(500);

                        // V8.6修复: 直接从 model 调用 SelectByID2，不使用 Extension
                        LogWarning("V8.9: 步骤2 - 调用 model.SelectByID2");
                        try
                        {
                            // 直接从 ModelDoc2 调用，不通过 Extension
                            selected = dynamicModel.SelectByID2(planeName, "PLANE", 0.0, 0.0, 0.0, false, 0, null, 0);
                            LogWarning("V8.9: 步骤2 - SelectByID2 完成，结果: " + selected);
                        }
                        catch (Exception selectEx)
                        {
                            LogWarning("V8.9: 步骤2 - SelectByID2 异常: " + selectEx.Message);

                            // 如果直接调用失败，尝试通过 Extension
                            LogWarning("V8.9: 步骤3 - 尝试通过 Extension.SelectByID2");
                            try
                            {
                                dynamic dynamicExtension = dynamicModel.Extension;
                                selected = dynamicExtension.SelectByID2(planeName, "PLANE", 0.0, 0.0, 0.0, false, 0, null, 0);
                                LogWarning("V8.9: 步骤3 - Extension.SelectByID2 完成，结果: " + selected);
                            }
                            catch (Exception exEx)
                            {
                                LogWarning("V8.9: 步骤3 - Extension.SelectByID2 异常: " + exEx.Message);
                                continue;  // 尝试下一个基准面名称
                            }
                        }

                        if (selected)
                        {
                            LogWarning("V8.9: 基准面 '" + planeName + "' 选择成功");

                            // V8.7修复: 延迟获取 SketchManager，在需要时才获取
                            LogWarning("V8.9: 步骤4 - 延迟获取 SketchManager");
                            try
                            {
                                dynamicSketchMgr = dynamicModel.SketchManager;
                                LogWarning("V8.9: 步骤4 - SketchManager 直接获取成功");
                            }
                            catch
                            {
                                LogWarning("V8.9: 步骤4 - 直接获取失败，尝试 Extension");
                                try
                                {
                                    dynamic dynamicExtension = dynamicModel.Extension;
                                    dynamicSketchMgr = dynamicExtension.SketchManager;
                                    LogWarning("V8.9: 步骤4 - 通过 Extension 获取 SketchManager 成功");
                                }
                                catch
                                {
                                    LogWarning("V8.9: 步骤4 - 所有方法获取 SketchManager 失败");
                                    lastError = "无法获取 SketchManager";
                                    return false;
                                }
                            }

                            // 使用dynamic调用InsertSketch
                            bool inserted = dynamicSketchMgr.InsertSketch(true);
                            if (inserted)
                            {
                                inSketch = true;
                                sketchMgr = dynamicSketchMgr;  // 保存强类型引用
                                lastError = "";
                                string successMsg = "V8.9成功: 在 '" + planeName + "' 上创建草图";
                                LogSuccess(successMsg);
                                return true;
                            }
                            else
                            {
                                LogWarning("V8.9: InsertSketch返回False");
                            }
                        }
                        else
                        {
                            LogWarning("V8.9: SelectByID2返回False");
                        }
                    }
                    catch (Exception ex)
                    {
                        LogWarning("V8.9: 基准面 '" + planeName + "' 异常: " + ex.Message);
                    }
                }

                // 如果选择基准面失败，尝试直接InsertSketch
                if (!sketchCreated)
                {
                    LogWarning("V8.9: 所有基准面选择失败，尝试直接InsertSketch");

                    // V8.7修复: 延迟获取 SketchManager
                    LogWarning("V8.9: 步骤5 - 延迟获取 SketchManager（直接InsertSketch）");
                    try
                    {
                        dynamicSketchMgr = dynamicModel.SketchManager;
                        LogWarning("V8.9: 步骤5 - SketchManager 直接获取成功");
                    }
                    catch
                    {
                        try
                        {
                            dynamic dynamicExtension = dynamicModel.Extension;
                            dynamicSketchMgr = dynamicExtension.SketchManager;
                            LogWarning("V8.7: 通过 Extension 获取 SketchManager 成功");
                        }
                        catch
                        {
                            LogWarning("V8.7: 无法获取 SketchManager");
                            lastError = "无法获取 SketchManager";
                            return false;
                        }
                    }

                    try
                    {
                        bool directInserted = dynamicSketchMgr.InsertSketch(true);
                        if (directInserted)
                        {
                            inSketch = true;
                            sketchMgr = dynamicSketchMgr;
                            lastError = "";
                            LogSuccess("V8成功: 直接创建草图（无基准面选择）");
                            return true;
                        }
                        else
                        {
                            LogWarning("V8: 直接InsertSketch返回False");
                        }
                    }
                    catch (Exception ex)
                    {
                        LogWarning("V8: 直接InsertSketch异常: " + ex.Message);
                    }
                }

                // 所有方法都失败
                string diagnosticInfo = lastError;
                lastError = "V8: 所有草图创建方法都失败\n\n详细诊断：\n" + diagnosticInfo;
                return false;
            }
            catch (Exception ex)
            {
                lastError = "创建草图错误: " + ex.Message;
                return false;
            }
        }

        public bool CreateSketchViaVBA()
        {
            lastOperation = "CreateSketchViaVBA";

            if (!ValidateConnection())
            {
                lastError = "未连接到SolidWorks";
                return false;
            }

            try
            {
                // 使用VBA宏创建草图
                // 方法1: 尝试前视基准面
                try
                {
                    // RunMacro需要3个参数：macroName, moduleName, procedureName
                    // 由于我们不需要实际宏文件，这里改为直接调用API
                    LogWarning("尝试直接使用SolidWorks API创建草图");
                    bool selected = model.Extension.SelectByID2("Front Plane", "PLANE", 0.0, 0.0, 0.0, false, 0, null, 0);
                    if (selected)
                    {
                        bool inserted = sketchMgr.InsertSketch(true);
                        if (inserted)
                        {
                            inSketch = true;
                            lastError = "";
                            LogSuccess("VBA宏成功: 在前视基准面创建草图");
                            return true;
                        }
                    }
                }
                catch (Exception ex1)
                {
                    LogWarning("直接API调用失败: " + ex1.Message);

                    // 方法2: 尝试使用不同的基准面名称
                    try
                    {
                        // 尝试多个基准面名称
                        object model = swApp.ActiveDoc;
                        if (model == null)
                        {
                            lastError = "没有活动文档";
                            return false;
                        }

                        // 获取Extension和SketchManager（使用late binding）
                        object extension = model.GetType().InvokeMember("Extension", System.Reflection.BindingFlags.GetProperty, null, model, null);
                        object sketchMgr = model.GetType().InvokeMember("SketchManager", System.Reflection.BindingFlags.GetProperty, null, model, null);

                        if (sketchMgr != null)
                        {
                            // 尝试多个基准面名称
                            string[] planeNames = { "Front Plane", "前视基准面", "Plane1" };
                            bool sketchCreated = false;

                            foreach (string planeName in planeNames)
                            {
                                try
                                {
                                    object[] args = { planeName, "PLANE", 0.0, 0.0, 0.0, false, 0, Type.Missing, 0 };
                                    object selected = extension.GetType().InvokeMember("SelectByID2",
                                        System.Reflection.BindingFlags.InvokeMethod, null, extension, args);

                                    if (selected != null && (bool)selected)
                                    {
                                        object[] insertArgs = { true };
                                        object inserted = sketchMgr.GetType().InvokeMember("InsertSketch",
                                            System.Reflection.BindingFlags.InvokeMethod, null, sketchMgr, insertArgs);

                                        if (inserted != null && (bool)inserted)
                                        {
                                            inSketch = true;
                                            lastError = "";
                                            string successMsg = "VBA late binding成功: 在 '" + planeName + "' 创建草图";
                                            LogSuccess(successMsg);
                                            return true;
                                        }
                                    }
                                }
                                catch { }
                            }
                        }
                    }
                    catch (Exception ex2)
                    {
                        LogWarning("VBA late binding失败: " + ex2.Message);
                    }
                }

                lastError = "VBA宏方法失败（已尝试多种方法）";
                return false;
            }
            catch (Exception ex)
            {
                lastError = "VBA调用异常: " + ex.Message;
                return false;
            }
        }

        public bool CloseSketch()
        {
            lastOperation = "CloseSketch";

            if (!ValidateDocument())
            {
                return false;
            }

            try
            {
                if (inSketch || sketchMgr != null)
                {
                    sketchMgr.InsertSketch(true);
                    inSketch = false;
                    LogSuccess("Closed sketch");
                }
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "关闭草图错误: " + ex.Message;
                return false;
            }
        }

        public bool InSketchMode()
        {
            return inSketch;
        }

        /// <summary>
        /// 绘制矩形 - 带参数验证
        /// </summary>
        public bool DrawRectangle(double x1, double y1, double x2, double y2)
        {
            lastOperation = "DrawRectangle";

            if (!ValidateSketch())
            {
                return false;
            }

            try
            {
                // 参数验证
                if (!ValidateCoordinates(x1, y1, x2, y2))
                {
                    return false;
                }

                double centerX = (x1 + x2) / 2.0;
                double centerY = (y1 + y2) / 2.0;
                double halfWidth = Math.Abs(x2 - x1) / 2.0;
                double halfHeight = Math.Abs(y2 - y1) / 2.0;

                sketchMgr.CreateCenterRectangle(centerX, centerY, 0, centerX + halfWidth, centerY + halfHeight, 0);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "绘制矩形错误: " + ex.Message;
                return false;
            }
        }

        public bool DrawCircle(double centerX, double centerY, double radius)
        {
            lastOperation = "DrawCircle";

            if (!ValidateSketch())
            {
                return false;
            }

            try
            {
                // 参数验证
                if (radius <= 0)
                {
                    lastError = "半径必须大于0";
                    return false;
                }

                if (double.IsInfinity(centerX) || double.IsInfinity(centerY) || double.IsInfinity(radius))
                {
                    lastError = "坐标或半径无效";
                    return false;
                }

                sketchMgr.CreateCircle(centerX, centerY, 0, radius);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "绘制圆形错误: " + ex.Message;
                return false;
            }
        }

        public bool DrawLine(double x1, double y1, double x2, double y2)
        {
            lastOperation = "DrawLine";

            if (!ValidateSketch())
            {
                return false;
            }

            try
            {
                // 参数验证
                if (!ValidateCoordinates(x1, y1, x2, y2))
                {
                    return false;
                }

                sketchMgr.CreateLine(x1, y1, 0, x2, y2, 0);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "绘制直线错误: " + ex.Message;
                return false;
            }
        }

        public bool CreateExtrusion(double depth)
        {
            lastOperation = "CreateExtrusion";

            if (!ValidateDocument())
            {
                return false;
            }

            try
            {
                // 参数验证
                if (depth <= 0)
                {
                    lastError = "深度必须大于0";
                    return false;
                }

                if (inSketch)
                {
                    CloseSketch();
                }

                dynamic feature = featureMgr.FeatureExtrusion(
                    true, false, false, false, false,
                    true, false, false, 0.0, 0.0, depth
                );

                if (feature == null)
                {
                    lastError = "无法创建拉伸特征";
                    return false;
                }

                LogSuccess("Created extrusion, depth: " + depth);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建拉伸错误: " + ex.Message;
                return false;
            }
        }

        public bool CreateCut(double depth)
        {
            lastOperation = "CreateCut";

            if (!ValidateDocument())
            {
                return false;
            }

            try
            {
                if (depth <= 0)
                {
                    lastError = "深度必须大于0";
                    return false;
                }

                if (inSketch)
                {
                    CloseSketch();
                }

                dynamic feature = featureMgr.FeatureCut(
                    true, false, false, false, false,
                    true, false, false, 0.0, 0.0, depth,
                    false, false, 0.0
                );

                if (feature == null)
                {
                    lastError = "无法创建切除特征";
                    return false;
                }

                LogSuccess("Created cut, depth: " + depth);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建切除错误: " + ex.Message;
                return false;
            }
        }

        public bool CreateChamfer(double distance, double angle)
        {
            lastOperation = "CreateChamfer";

            if (!ValidateDocument())
            {
                return false;
            }

            try
            {
                // 参数验证
                if (distance <= 0)
                {
                    lastError = "距离必须大于0";
                    return false;
                }

                if (angle <= 0 || angle >= 90)
                {
                    lastError = "角度必须在0-90度之间";
                    return false;
                }

                dynamic feature = featureMgr.FeatureChamfer(
                    1, distance, angle, 0.0, false, 0
                );

                if (feature == null)
                {
                    lastError = "无法创建倒角";
                    return false;
                }

                LogSuccess("Created chamfer");
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建倒角错误: " + ex.Message;
                return false;
            }
        }

        public bool CreateInternalThread(double diameter, double pitch, double length)
        {
            lastOperation = "CreateInternalThread";

            if (!ValidateDocument())
            {
                return false;
            }

            try
            {
                // 参数验证
                if (diameter <= 0)
                {
                    lastError = "直径必须大于0";
                    return false;
                }

                if (pitch <= 0)
                {
                    lastError = "螺距必须大于0";
                    return false;
                }

                if (length <= 0)
                {
                    lastError = "长度必须大于0";
                    return false;
                }

                dynamic feature = featureMgr.FeatureCutThreading(
                    true, false, false, false, false,
                    true, false, false, 0.0, 0.0, length,
                    false, false, 0.0,
                    diameter, pitch, 0.0, 60.0,
                    false, false, 0, 0.0
                );

                if (feature == null)
                {
                    lastError = "无法创建内螺纹";
                    return false;
                }

                LogSuccess("Created internal thread M" + diameter + "x" + pitch);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建内螺纹错误: " + ex.Message;
                return false;
            }
        }

        public string GetLastError()
        {
            return lastError;
        }

        public string GetLastOperation()
        {
            return lastOperation;
        }

        public bool GetConnectionHealth()
        {
            return IsSWConnected() && model != null && sketchMgr != null && featureMgr != null;
        }

        // ==================== 私有辅助方法 ====================

        private void InitializeManagers()
        {
            if (model != null)
            {
                // V8.4修复: 使用 dynamic 延迟绑定避免 DISP_E_BADINDEX
                // model 刚创建后，某些属性可能还未准备好
                try
                {
                    // 方法1: 尝试直接访问
                    sketchMgr = model.SketchManager;
                    LogWarning("V8.4: SketchManager 直接访问成功");
                }
                catch
                {
                    // 方法2: 使用 dynamic 访问
                    try
                    {
                        dynamic dynamicModel = model;
                        sketchMgr = (SketchManager)dynamicModel.SketchManager;
                        LogWarning("V8.4: SketchManager dynamic 访问成功");
                    }
                    catch
                    {
                        LogWarning("V8.4: SketchManager 获取失败，将在需要时重试");
                        sketchMgr = null;
                    }
                }

                try
                {
                    featureMgr = model.FeatureManager;
                    LogWarning("V8.4: FeatureManager 直接访问成功");
                }
                catch
                {
                    try
                    {
                        dynamic dynamicModel = model;
                        featureMgr = (FeatureManager)dynamicModel.FeatureManager;
                        LogWarning("V8.4: FeatureManager dynamic 访问成功");
                    }
                    catch
                    {
                        LogWarning("V8.4: FeatureManager 获取失败，将在需要时重试");
                        featureMgr = null;
                    }
                }
            }
        }

        private bool ValidateConnection()
        {
            if (!IsSWConnected())
            {
                lastError = "未连接到SolidWorks";
                return false;
            }
            return true;
        }

        private bool ValidateDocument()
        {
            if (!ValidateConnection())
            {
                return false;
            }

            if (model == null)
            {
                lastError = "没有活动文档";
                return false;
            }

            return true;
        }

        private bool ValidateSketch()
        {
            if (!ValidateDocument())
            {
                return false;
            }

            if (sketchMgr == null)
            {
                lastError = "草图管理器未初始化";
                return false;
            }

            if (!inSketch)
            {
                lastError = "不在草图模式";
                return false;
            }

            return true;
        }

        private bool ValidateCoordinates(double x1, double y1, double x2, double y2)
        {
            if (double.IsInfinity(x1) || double.IsInfinity(y1) ||
                double.IsInfinity(x2) || double.IsInfinity(y2))
            {
                lastError = "坐标包含无限值";
                return false;
            }

            if (double.IsNaN(x1) || double.IsNaN(y1) ||
                double.IsNaN(x2) || double.IsNaN(y2))
            {
                lastError = "坐标包含NaN";
                return false;
            }

            return true;
        }

        private void LogSuccess(string message)
        {
            lastOperation = message;

            // V8.3: 写入文件日志
            try
            {
                string logFile = @"D:\sw2026\代码\SWHelper\debug_log.txt";
                string timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                string logMessage = "[" + timestamp + "] SUCCESS: " + message + "\n";
                System.IO.File.AppendAllText(logFile, logMessage);
            }
            catch
            {
                // 忽略日志错误
            }
        }

        private void LogWarning(string message)
        {
            // V8.3: 使用文件日志代替 Debug.WriteLine
            try
            {
                string logFile = @"D:\sw2026\代码\SWHelper\debug_log.txt";
                string timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                string logMessage = "[" + timestamp + "] WARNING: " + message + "\n";
                System.IO.File.AppendAllText(logFile, logMessage);
            }
            catch
            {
                // 忽略日志错误
            }

            // 同时累积到 lastError
            if (string.IsNullOrEmpty(lastError))
            {
                lastError = "DIAGNOSTICS:\n";
            }
            lastError += "- " + message + "\n";
        }

        private void LogError(string message)
        {
            // V8.3: 使用文件日志代替 Debug.WriteLine
            try
            {
                string logFile = @"D:\sw2026\代码\SWHelper\debug_log.txt";
                string timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                string logMessage = "[" + timestamp + "] ERROR: " + message + "\n";
                System.IO.File.AppendAllText(logFile, logMessage);
            }
            catch
            {
                // 忽略日志错误
            }

            lastError = message;
        }
    }
}
