// 临时调试版本：添加详细日志输出
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

namespace SWHelper
{
    [Guid("YOUR-GUID-HERE")]
    [ComVisible(true)]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class SWHelperDebug
    {
        private SldWorks swApp;
        private ModelDoc2 model;
        private SketchManager sketchMgr;
        private bool isConnected;
        private string lastError = "";

        public string GetVersion() => "SWHelper Debug V1";

        public bool ConnectToSW()
        {
            try
            {
                swApp = new SldWorks();
                model = swApp.ActiveDoc as ModelDoc2;

                if (model != null)
                {
                    int docType = model.GetType_();
                    Debug.WriteLine($"Document type: {docType}");

                    if (docType == 1)  // 零件
                    {
                        sketchMgr = model.SketchManager;
                        isConnected = true;
                        return true;
                    }
                    else
                    {
                        lastError = $"文档类型不是零件: {docType}";
                        return false;
                    }
                }
                else
                {
                    lastError = "没有活动文档";
                    return false;
                }
            }
            catch (Exception ex)
            {
                lastError = $"连接异常: {ex.Message}";
                return false;
            }
        }

        public bool CreateSketch()
        {
            if (model == null)
            {
                lastError = "没有活动文档";
                return false;
            }

            if (sketchMgr == null)
            {
                lastError = "草图管理器未初始化";
                return false;
            }

            // 方案1: Front Plane (English)
            Debug.WriteLine("=== 尝试方案1: Front Plane (English) ===");
            try
            {
                object callout = Type.Missing;
                bool selected = model.Extension.SelectByID2("Front Plane", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout, 0);
                Debug.WriteLine($"SelectByID2返回: {selected}");

                if (selected)
                {
                    bool inserted = sketchMgr.InsertSketch(true);
                    Debug.WriteLine($"InsertSketch返回: {inserted}");
                    if (inserted) return true;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"方案1异常: {ex.Message}");
                lastError = $"方案1: {ex.Message}";
            }

            // 方案2: 前视基准面 (Chinese)
            Debug.WriteLine("=== 尝试方案2: 前视基准面 (Chinese) ===");
            try
            {
                object callout = Type.Missing;
                bool selected = model.Extension.SelectByID2("前视基准面", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout, 0);
                Debug.WriteLine($"SelectByID2返回: {selected}");

                if (selected)
                {
                    bool inserted = sketchMgr.InsertSketch(true);
                    Debug.WriteLine($"InsertSketch返回: {inserted}");
                    if (inserted) return true;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"方案2异常: {ex.Message}");
                lastError = $"方案2: {ex.Message}";
            }

            // 方案3: Plane1
            Debug.WriteLine("=== 尝试方案3: Plane1 ===");
            try
            {
                object callout = Type.Missing;
                bool selected = model.Extension.SelectByID2("Plane1", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout, 0);
                Debug.WriteLine($"SelectByID2返回: {selected}");

                if (selected)
                {
                    bool inserted = sketchMgr.InsertSketch(true);
                    Debug.WriteLine($"InsertSketch返回: {inserted}");
                    if (inserted) return true;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"方案3异常: {ex.Message}");
                lastError = $"方案3: {ex.Message}";
            }

            // 方案4: 直接插入草图
            Debug.WriteLine("=== 尝试方案4: 直接InsertSketch ===");
            try
            {
                bool inserted = sketchMgr.InsertSketch(true);
                Debug.WriteLine($"InsertSketch返回: {inserted}");
                if (inserted) return true;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"方案4异常: {ex.Message}");
                lastError = $"方案4: {ex.Message}";
            }

            lastError = "所有方案都失败";
            return false;
        }

        public string GetLastError() => lastError;

        public bool HasActiveDocument()
        {
            try
            {
                return swApp != null && swApp.ActiveDoc != null;
            }
            catch
            {
                return false;
            }
        }

        public string GetSystemStatus()
        {
            return $"Debug Version\nConnected: {isConnected}\nHas Document: {HasActiveDocument()}\nLast Error: {lastError}";
        }
    }
}
