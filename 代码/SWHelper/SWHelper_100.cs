using System;
using SolidWorks.Interop.sldworks;

namespace SWHelper
{
    /// <summary>
    /// SWHelper 100%版本接口
    /// 实现完整的自动化功能，包括最后5%
    /// </summary>
    [System.Runtime.InteropServices.ComVisible(true)]
    public interface ISWHelper100
    {
        bool ConnectToSW();
        bool CreatePart();
        bool CreateSketch();
        bool DrawRectangle(double x1, double y1, double x2, double y2);
        bool CloseSketch();

        // 最后5%功能 - 关键方法
        bool SelectSketch(string sketchName);
        bool CreateExtrusion(double depth);

        string GetVersion();
        string GetLastError();
    }

    /// <summary>
    /// SWHelper 100%版本实现
    /// 解决Python COM类型不兼容问题，实现100%自动化
    /// </summary>
    [System.Runtime.InteropServices.ComVisible(true)]
    public class SWHelper100 : ISWHelper100
    {
        private SldWorks swApp;
        private ModelDoc2 model;
        private SketchManager sketchMgr;
        private FeatureManager featureMgr;
        private string lastError = "";

        public bool ConnectToSW()
        {
            try
            {
                // 尝试连接现有SolidWorks实例
                swApp = (SldWorks)System.Runtime.InteropServices.Marshal.GetActiveObject("SldWorks.Application");
                if (swApp != null)
                {
                    lastError = "";
                    return true;
                }

                // 创建新实例
                swApp = new SldWorks();
                if (swApp != null)
                {
                    swApp.Visible = true;
                    lastError = "";
                    return true;
                }

                lastError = "无法连接SolidWorks";
                return false;
            }
            catch (Exception ex)
            {
                lastError = "连接错误: " + ex.Message;
                return false;
            }
        }

        public bool CreatePart()
        {
            try
            {
                if (swApp == null && !ConnectToSW())
                {
                    return false;
                }

                string templatePath = swApp.GetUserPreferenceStringValue(4); // swDefaultTemplatePart
                ModelDoc2 newDoc = (ModelDoc2)swApp.NewDocument(templatePath, 0, 0, 0);

                if (newDoc == null)
                {
                    lastError = "无法创建零件";
                    return false;
                }

                model = newDoc;
                sketchMgr = model.SketchManager;
                featureMgr = model.FeatureManager;

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建零件错误: " + ex.Message;
                return false;
            }
        }

        public bool CreateSketch()
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开文档";
                    return false;
                }

                bool selected = model.Extension.SelectByID2("前视基准面", "PLANE", 0, 0, 0, false, 0, null, 0);
                if (!selected)
                {
                    lastError = "无法选择基准面";
                    return false;
                }

                sketchMgr.InsertSketch(true);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建草图错误: " + ex.Message;
                return false;
            }
        }

        public bool DrawRectangle(double x1, double y1, double x2, double y2)
        {
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
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

        public bool CloseSketch()
        {
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
                    return false;
                }

                sketchMgr.InsertSketch(true);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "关闭草图错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 关键方法：选择草图 - 解决Python COM类型不兼容问题
        /// 这是实现100%自动化的核心突破
        /// </summary>
        public bool SelectSketch(string sketchName)
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开文档";
                    return false;
                }

                // 关键突破：使用C#正确处理COM类型
                Callout callout = null;

                bool selected = model.Extension.SelectByID2(
                    sketchName,      // 草图名称
                    "SKETCH",         // 类型
                    0, 0, 0,          // 坐标
                    false,            // append
                    0,                // mark
                    callout,          // 关键参数！C#正确处理COM类型
                    0                 // calloutInsertRef
                );

                if (!selected)
                {
                    lastError = "无法选择草图: " + sketchName;
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "选择草图错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 关键方法：创建拉伸特征 - 实现100%自动化的最后5%
        /// 使用简化的FeatureExtrusion方法而不是FeatureExtrusion2
        /// </summary>
        public bool CreateExtrusion(double depth)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 使用最简化的拉伸方法（2个参数）
                Feature feature = (Feature)featureMgr.FeatureExtrusion(
                    true,    // directionOne
                    depth    // depth - 拉伸深度
                );

                if (feature == null)
                {
                    lastError = "无法创建拉伸特征，深度: " + depth;
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建拉伸错误: " + ex.Message;
                return false;
            }
        }

        public string GetVersion()
        {
            return "SWHelper v1.0-Full (100% Automation)";
        }

        public string GetLastError()
        {
            return lastError;
        }
    }
}
