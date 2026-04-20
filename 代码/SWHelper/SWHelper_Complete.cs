using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

namespace SWHelper
{
    /// <summary>
    /// SWHelper完整接口 - 100%自动化
    /// </summary>
    [ComVisible(true)]
    public interface ISWHelperComplete
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
    /// SWHelper完整实现 - 100%自动化
    /// 使用反射调用SolidWorks API，避免编译器兼容性问题
    /// </summary>
    [ComVisible(true)]
    public class SWHelperComplete : ISWHelperComplete
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
                swApp = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");
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
        /// 核心突破：SelectSketch方法 - 解决Python COM类型不兼容
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

                // 关键：使用反射找到正确的重载方法
                Type[] selectParamTypes = new Type[] {
                    typeof(string), typeof(string), typeof(double), typeof(double), typeof(double),
                    typeof(bool), typeof(int), typeof(object).MakeByRefType(), typeof(int)
                };
                MethodInfo selectMethod = model.Extension.GetType().GetMethod("SelectByID2", selectParamTypes);

                if (selectMethod == null)
                {
                    lastError = "找不到SelectByID2方法";
                    return false;
                }

                object callout = null;
                object[] parameters = new object[] { sketchName, "SKETCH", 0, 0, 0, false, 0, callout, 0 };

                object result = selectMethod.Invoke(model.Extension, parameters);
                bool selected = (bool)result;

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
        /// 核心突破：CreateExtrusion方法 - 实现100%自动化
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

                // 使用反射调用FeatureExtrusion2方法
                // 尝试不同参数数量的重载
                MethodInfo extrudeMethod = null;
                object result = null;

                // 尝试54参数版本
                extrudeMethod = featureMgr.GetType().GetMethod("FeatureExtrusion2");
                if (extrudeMethod != null)
                {
                    ParameterInfo[] params = extrudeMethod.GetParameters();
                    int paramCount = params.Length;

                    // 创建参数数组 - 使用默认值
                    object[] parameters = new object[paramCount];
                    parameters[0] = true;   // directionOne
                    parameters[4] = false;  // useDefaultOffset
                    parameters[5] = false;  // useFeatureScope
                    parameters[6] = false;  // useAutoSelect
                    parameters[7] = true;   // maintainTangentChain
                    parameters[8] = false;  // isThinFeature
                    parameters[9] = false;  // isDraftFeature
                    parameters[10] = 0.0;   // draftAngle
                    parameters[11] = 0.0;   // offset
                    parameters[12] = depth;  // depth - 关键参数
                    parameters[13] = 0.0;  // depth2
                    parameters[14] = false; // reverseDirection
                    parameters[15] = false; // useCapPlane
                    parameters[16] = 0.0;   // capPlaneOffset
                    parameters[17] = 0.0;   // depth3
                    parameters[18] = false; // reverseDirection2
                    parameters[19] = false; // useCapPlane2
                    parameters[20] = 0.0;   // capPlaneOffset2
                    parameters[21] = 0.0;   // depth4
                    parameters[22] = false; // reverseDirection3
                    parameters[23] = true;  // combineBodies
                    parameters[24] = true;  // isContourMerge
                    parameters[25] = false; // isContourMergeAll

                    // 填充剩余参数
                    for (int i = 26; i < paramCount; i++)
                    {
                        Type paramType = extrudeMethod.GetParameters()[i].ParameterType;
                        if (paramType == typeof(bool))
                            parameters[i] = false;
                        else if (paramType == typeof(int))
                            parameters[i] = 0;
                        else if (paramType == typeof(double))
                            parameters[i] = 0.0;
                        else
                            parameters[i] = null;
                    }

                    result = extrudeMethod.Invoke(featureMgr, parameters);
                    Feature feature = (Feature)result;

                    if (feature == null)
                    {
                        lastError = "无法创建拉伸特征，深度: " + depth;
                        return false;
                    }

                    lastError = "";
                    return true;
                }

                lastError = "找不到FeatureExtrusion2方法";
                return false;
            }
            catch (Exception ex)
            {
                lastError = "创建拉伸错误: " + ex.Message;
                return false;
            }
        }

        public string GetVersion()
        {
            return "SWHelper v1.0-Complete (100% Automation)";
        }

        public string GetLastError()
        {
            return lastError;
        }
    }
}
