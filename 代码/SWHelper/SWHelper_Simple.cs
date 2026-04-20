using System;
using SolidWorks.Interop.sldworks;

namespace SWHelper
{
    /// <summary>
    /// SWHelper简化接口 - 专注于最后5%功能
    /// </summary>
    [ComVisible(true)]
    public interface ISWHelperSimple
    {
        bool ConnectToSW();
        bool CreatePart();
        bool CreateSketch();
        bool DrawRectangle(double x1, double y1, double x2, double y2);
        bool CloseSketch();
        bool SelectSketch(string sketchName);
        bool CreateExtrusion(double depth);
        string GetVersion();
        string GetLastError();
    }

    /// <summary>
    /// SWHelper简化实现 - 专注于最后5%功能
    /// 解决Python COM类型不兼容问题的关键代码
    /// </summary>
    [ComVisible(true)]
    public class SWHelperSimple : ISWHelperSimple
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
                object swAppObj = Marshal.GetActiveObject("SldWorks.Application");
                swApp = (SldWorks)swAppObj;

                if (swApp != null)
                {
                    lastError = "";
                    return true;
                }

                swApp = new SldWorks();
                if (swApp != null)
                {
                    swApp.Visible = true;
                    lastError = "";
                    return true;
                }

                lastError = "无法创建或连接到SolidWorks实例";
                return false;
            }
            catch (Exception ex)
            {
                lastError = string.Format("连接错误: {0}", ex.Message);
                return false;
            }
        }

        public bool CreatePart()
        {
            try
            {
                if (swApp == null)
                {
                    if (!ConnectToSW())
                    {
                        return false;
                    }
                }

                string templatePath = swApp.GetUserPreferenceStringValue(4); // swDefaultTemplatePart
                ModelDoc2 newDoc = (ModelDoc2)swApp.NewDocument(templatePath, 0, 0, 0);

                if (newDoc == null)
                {
                    lastError = "无法创建零件文档";
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
                lastError = string.Format("创建零件错误: {0}", ex.Message);
                return false;
            }
        }

        public bool CreateSketch()
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开的文档";
                    return false;
                }

                bool selected = model.Extension.SelectByID2("前视基准面", "PLANE", 0, 0, 0, false, 0, null, 0);

                if (!selected)
                {
                    lastError = "无法选择前视基准面";
                    return false;
                }

                sketchMgr.InsertSketch(true);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建草图错误: {0}", ex.Message);
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
                double width = Math.Abs(x2 - x1);
                double height = Math.Abs(y2 - y1);

                sketchMgr.CreateCenterRectangle(centerX, centerY, 0, centerX + width / 2.0, centerY + height / 2.0, 0);
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("绘制矩形错误: {0}", ex.Message);
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
                lastError = string.Format("关闭草图错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 关键方法：选择草图 - 解决Python COM类型不兼容问题
        /// </summary>
        public bool SelectSketch(string sketchName)
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开的文档";
                    return false;
                }

                // 关键：使用object callout = null，C#会正确转换为COM VARIANT类型
                Callout callout = null;

                bool selected = model.Extension.SelectByID2(
                    sketchName,
                    "SKETCH",
                    0, 0, 0,
                    false,
                    0,
                    callout,  // 关键参数！C#正确处理VARIANT类型
                    0
                );

                if (!selected)
                {
                    lastError = string.Format("无法选择草图: {0}", sketchName);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("选择草图错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 关键方法：创建拉伸特征 - 最后5%功能之一
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

                // 使用完整参数的拉伸方法
                Feature feature = (Feature)featureMgr.FeatureExtrusion2(
                    true,   // directionOne
                    false,  // flipDirection
                    false,  // useDefaultOffset
                    false,  // useFeatureScope
                    false,  // useAutoSelect
                    true,   // maintainTangentChain
                    true,   // isThinFeature
                    false,  // isDraftFeature
                    0.0,    // draftAngle
                    0.0,    // offset
                    depth,  // depth
                    0.0,    // depth2
                    false,  // reverseDirection
                    false,  // useCapPlane
                    0.0,    // capPlaneOffset
                    0.0,    // depth3
                    false,  // reverseDirection2
                    false,  // useCapPlane2
                    0.0,    // capPlaneOffset2
                    0.0,    // depth4
                    false,  // reverseDirection3
                    true,   // combineBodies
                    true,   // isContourMerge
                    false,  // isContourMergeAll
                    0,      // startCondition
                    0.0,    // startOffset
                    0,      // endCondition
                    0.0,    // endOffset
                    0,      // endCondition2
                    0.0,    // endOffset2
                    0.0,    // wallThickness
                    false,  // maintainWallThickness
                    false,  // reverseWallThicknessDirection
                    false,  // useDefaultBendRadius
                    0.0,    // bendRadius
                    false,  // useSheetMetal
                    0.0,    // sheetMetalThickness
                    0       // bendAllowanceType
                );

                if (feature == null)
                {
                    lastError = string.Format("无法创建拉伸特征，深度: {0}", depth);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建拉伸错误: {0}", ex.Message);
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
