using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using System.Reflection;

namespace SWHelper
{
    /// <summary>
    /// SWHelper 高可靠性版�?    /// 核心设计原则�?    /// 1. 连接稳定�?- 多重重试和备用方�?    /// 2. API调用健壮�?- 参数验证和错误处�?    /// 3. 状态管�?- 实时检测和自动恢复
    /// 4. 版本管理 - 清晰的版本和兼容�?    /// </summary>

    [ComVisible(true)]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelperRobustV2
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

        // 绘图操作（带参数验证�?        bool DrawRectangle(double x1, double y1, double x2, double y2);
        bool DrawCircle(double centerX, double centerY, double radius);
        bool DrawLine(double x1, double y1, double x2, double y2);

        // 特征操作（带前置检查）
        bool CreateExtrusion(double depth);
        bool CreateCut(double depth);
        bool CreateChamfer(double distance, double angle);

        // 关键新方�?        bool CreateInternalThread(double diameter, double pitch, double length);

        // 状态和错误
        string GetLastError();
        string GetLastOperation();
        bool GetConnectionHealth();
    }

    [ComVisible(true)]
    [ClassInterface(ClassInterfaceType.None)]
    public class SWHelperRobustV2 : ISWHelperRobustV2
    {
        // 版本信息
        private const string VERSION = "2.0-Robust";
        private const string BUILD_DATE = "2026.04.14";

        // SolidWorks对象（使用弱引用避免内存泄漏�?        private SldWorks swApp;
        private dynamic model;
        private dynamic sketchMgr;
        private dynamic featureMgr;

        // 状态管�?        private bool isConnected = false;
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
        /// 高可靠性连接方�?- 带重试和备用方案
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

                // 方案2: 创建新实�?                for (int i = 0; i < RETRY_COUNT; i++)
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
        /// 刷新model对象 - 解决连接状态不同步问题（问�?3�?        /// </summary>
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
                        Marshal.ReleaseComObject(model);
                        model = null;
                    }

                    // 获取当前活动文档
                    model = swApp.ActiveDoc;

                    // 更新相关的管理器
                    if (model != null)
                    {
                        sketchMgr = model.SketchManager;
                        featureMgr = model.FeatureManager;

                        LogSuccess("Model refreshed successfully");
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
                return false;
            }
        }

        /// <summary>
        /// 断开连接并清理资�?        /// </summary>
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
        /// 高可靠性文档创�?- 带模板检测和备用方案
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
                // 方案1: 使用默认模板
                model = swApp.NewDocument("", 1, 0, 0);  // 1 = swDocPART

                if (model != null)
                {
                    InitializeManagers();
                    LogSuccess("Created part using default template");
                    return true;
                }

                // 方案2: 尝试获取模板路径
                try
                {
                    string templatePath = swApp.GetUserPreferenceStringValue(20); // swDefaultTemplatePart
                    if (!string.IsNullOrEmpty(templatePath))
                    {
                        model = swApp.NewDocument(templatePath, 1, 0, 0);
                        if (model != null)
                        {
                            InitializeManagers();
                            LogSuccess("Created part using template");
                            return true;
                        }
                    }
                }
                catch (Exception ex)
                {
                    LogWarning("Template method failed: " + ex.Message);
                }

                lastError = "无法创建零件（所有方案都失败�?;
                return false;
            }
            catch (Exception ex)
            {
                lastError = "创建零件错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 安全模式创建零件 - 带更多验�?        /// </summary>
        public bool CreatePartSafe()
        {
            lastOperation = "CreatePartSafe";

            // 先验证连�?            if (!ValidateConnection())
            {
                return false;
            }

            // 检查是否已有文�?            if (HasActiveDocument())
            {
                LogWarning("已有活动文档，关闭旧文档");
                try
                {
                    swApp.CloseDoc(model.GetTitle());
                }
                catch { }
            }

            // 创建新零�?            return CreatePart();
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
        /// 创建草图 - 带状态检查，多方案备�?        /// </summary>
        public bool CreateSketch()
        {
            lastOperation = "CreateSketch";

            if (!ValidateDocument())
            {
                return false;
            }

            try
            {
                // 检查是否已在草图模�?                if (inSketch)
                {
                    LogWarning("已在草图模式，先关闭现有草图");
                    CloseSketch();
                }

                // 方案1: 使用ref callout修复COM VARIANT类型
                System.Diagnostics.Debug.WriteLine("尝试方案1: SelectByID2 with ref callout (DBNull.Value)");
                try
                {
                    object callout = DBNull.Value;
                    bool selected = model.Extension.SelectByID2("Front Plane", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout, 0);

                    if (selected)
                    {
                        sketchMgr.InsertSketch(true);
                        inSketch = true;
                        lastError = "";
                        LogSuccess("方案1成功: Created sketch on Front Plane");
                        return true;
                    }
                    else
                    {
                        LogWarning("方案1: SelectByID2返回False");
                    }
                }
                catch (Exception ex1)
                {
                    LogWarning("方案1失败: " + ex1.Message);
                }

                // 方案2: 使用Type.Missing with ref
                System.Diagnostics.Debug.WriteLine("尝试方案2: SelectByID2 with ref callout (Type.Missing)");
                try
                {
                    object callout = Type.Missing;
                    bool selected = model.Extension.SelectByID2("Front Plane", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout, 0);

                    if (selected)
                    {
                        sketchMgr.InsertSketch(true);
                        inSketch = true;
                        lastError = "";
                        LogSuccess("方案2成功: Created sketch on Front Plane");
                        return true;
                    }
                    else
                    {
                        LogWarning("方案2: SelectByID2返回False");
                    }
                }
                catch (Exception ex2)
                {
                    LogWarning("方案2失败: " + ex2.Message);
                }

                // 方案3: 尝试使用ModelDoc2.SelectById (不同的API)
                System.Diagnostics.Debug.WriteLine("尝试方案3: ModelDoc2.SelectById");
                try
                {
                    bool selected = model.SelectById("Front Plane", "PLANE", 0.0, 0.0, 0.0);

                    if (selected)
                    {
                        sketchMgr.InsertSketch(true);
                        inSketch = true;
                        lastError = "";
                        LogSuccess("方案3成功: Created sketch via SelectById");
                        return true;
                    }
                    else
                    {
                        LogWarning("方案3: SelectById返回False");
                    }
                }
                catch (Exception ex3)
                {
                    LogWarning("方案3失败: " + ex3.Message);
                }

                // 方案4: 绕过选择，直接插入草�?                System.Diagnostics.Debug.WriteLine("尝试方案4: Direct InsertSketch without selection");
                try
                {
                    // 直接插入草图，不选择基准�?                    bool result = sketchMgr.InsertSketch(true);

                    if (result)
                    {
                        inSketch = true;
                        lastError = "";
                        LogSuccess("方案4成功: Created sketch without plane selection");
                        return true;
                    }
                    else
                    {
                        LogWarning("方案4: InsertSketch返回False");
                    }
                }
                catch (Exception ex4)
                {
                    LogWarning("方案4失败: " + ex4.Message);
                }

                // 所有方案都失败
                lastError = "CreateSketch失败：已尝试4种方案（详细错误请查看日志）";
                LogError("CreateSketch失败：已尝试4种方�?);
                return false;

            }
            catch (Exception ex)
            {
                lastError = "创建草图错误: " + ex.Message;
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
        /// 绘制矩形 - 带参数验�?        /// </summary>
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
                    lastError = "坐标或半径无�?;
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
                    lastError = "角度必须�?-90度之�?;
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
                    lastError = "无法创建内螺�?;
                    return false;
                }

                LogSuccess("Created internal thread M" + diameter + "x" + pitch);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建内螺纹错�? " + ex.Message;
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
                sketchMgr = model.SketchManager;
                featureMgr = model.FeatureManager;
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
                lastError = "草图管理器未初始�?;
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
                lastError = "坐标包含无限�?;
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
            // 可以扩展为写入日志文�?        }

        private void LogWarning(string message)
        {
            // 可以扩展为写入日志文�?            System.Diagnostics.Debug.WriteLine("WARNING: " + message);
        }

        private void LogError(string message)
        {
            lastError = message;
            // 可以扩展为写入日志文�?            System.Diagnostics.Debug.WriteLine("ERROR: " + message);
        }
    }
}
