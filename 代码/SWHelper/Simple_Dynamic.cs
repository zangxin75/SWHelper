using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

namespace SWHelper
{
    [ComVisible(true)]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelperDynamic
    {
        string GetVersion();
        string TestConnect();
        bool ConnectToSW();
        bool CreatePart();
        bool CreateSketch();
        bool DrawRectangle(double x1, double y1, double x2, double y2);
        bool CloseSketch();
        bool SelectSketch(string sketchName);
        bool CreateExtrusion(double depth);
        string GetLastError();
    }

    [ComVisible(true)]
    [ClassInterface(ClassInterfaceType.None)]
    public class SWHelperDynamic : ISWHelperDynamic
    {
        private dynamic swApp;
        private dynamic model;
        private dynamic sketchMgr;
        private dynamic featureMgr;
        private string version = "1.0-Full-Dynamic";
        private string lastError = "";

        public string GetVersion()
        {
            return "SWHelper v" + version + " (100% Automation with Dynamic Types)";
        }

        public string TestConnect()
        {
            return "SUCCESS: SWHelper完整版本编译和注册成功！";
        }

        public bool ConnectToSW()
        {
            try
            {
                swApp = Marshal.GetActiveObject("SldWorks.Application");
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

                string templatePath = swApp.GetUserPreferenceStringValue(4);
                model = swApp.NewDocument(templatePath, 0, 0, 0);

                if (model == null)
                {
                    lastError = "无法创建零件";
                    return false;
                }

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
        /// 核心突破：SelectSketch方法 - 使用dynamic避免类型问题
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

                // 使用dynamic避免类型检查问题
                dynamic callout = null;

                bool selected = model.Extension.SelectByID2(
                    sketchName,
                    "SKETCH",
                    0, 0, 0,
                    false,
                    0,
                    callout,
                    0
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
        /// 核心突破：CreateExtrusion方法 - 使用dynamic解决API兼容性
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

                // 使用dynamic调用，让运行时确定正确的重载
                dynamic feature = featureMgr.FeatureExtrusion(
                    true,    // directionOne
                    false,   // flipDirection
                    false,   // useDefaultOffset
                    false,   // useFeatureScope
                    false,   // useAutoSelect
                    true,    // maintainTangentChain
                    false,   // isThinFeature
                    false,   // isDraftFeature
                    0.0,     // draftAngle
                    0.0,     // offset
                    depth    // depth - 关键参数
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

        public string GetLastError()
        {
            return lastError;
        }
    }
}
