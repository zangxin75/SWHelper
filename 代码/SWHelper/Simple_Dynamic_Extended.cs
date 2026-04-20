using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

namespace SWHelper
{
    [ComVisible(true)]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelperDynamic
    {
        // 原有方法
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

        // ===== 新增方法 - 阶段2扩展 =====

        /// <summary>
        /// 绘制圆形
        /// </summary>
        /// <param name="centerX">圆心X坐标</param>
        /// <param name="centerY">圆心Y坐标</param>
        /// <param name="radius">半径</param>
        /// <returns>成功返回true</returns>
        bool DrawCircle(double centerX, double centerY, double radius);

        /// <summary>
        /// 绘制直线
        /// </summary>
        /// <param name="x1">起点X坐标</param>
        /// <param name="y1">起点Y坐标</param>
        /// <param name="x2">终点X坐标</param>
        /// <param name="y2">终点Y坐标</param>
        /// <returns>成功返回true</returns>
        bool DrawLine(double x1, double y1, double x2, double y2);

        /// <summary>
        /// 创建旋转特征
        /// </summary>
        /// <param name="angle">旋转角度（弧度）</param>
        /// <returns>成功返回true</returns>
        bool CreateRevolution(double angle);

        /// <summary>
        /// 创建圆角特征
        /// </summary>
        /// <param name="radius">圆角半径</param>
        /// <returns>成功返回true</returns>
        bool CreateFillet(double radius);

        /// <summary>
        /// 创建倒角特征
        /// </summary>
        /// <param name="distance">倒角距离</param>
        /// <param name="angle">倒角角度（度）</param>
        /// <returns>成功返回true</returns>
        bool CreateChamfer(double distance, double angle);

        /// <summary>
        /// 创建切除特征 - 用于通孔、盲孔等
        /// </summary>
        /// <param name="depth">切除深度</param>
        /// <returns>成功返回true</returns>
        bool CreateCut(double depth);

        /// <summary>
        /// 创建内螺纹特征 - 用于螺母等
        /// </summary>
        /// <param name="diameter">螺纹大径</param>
        /// <param name="pitch">螺距</param>
        /// <param name="length">螺纹长度</param>
        /// <returns>成功返回true</returns>
        bool CreateInternalThread(double diameter, double pitch, double length);
    }

    [ComVisible(true)]
    [ClassInterface(ClassInterfaceType.None)]
    public class SWHelperDynamic : ISWHelperDynamic
    {
        private dynamic swApp;
        private dynamic model;
        private dynamic sketchMgr;
        private dynamic featureMgr;
        private string version = "1.2-100Percent-Dynamic";  // 100%功能版本
        private string lastError = "";

        public string GetVersion()
        {
            return "SWHelper v" + version + " (Extended with Circle, Revolution, Fillet, Chamfer)";
        }

        public string TestConnect()
        {
            return "SUCCESS: SWHelper扩展版本编译和注册成功！支持圆形、旋转、圆角、倒角！";
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

        public bool SelectSketch(string sketchName)
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开文档";
                    return false;
                }

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

        public bool CreateExtrusion(double depth)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                dynamic feature = featureMgr.FeatureExtrusion(
                    true, false, false, false, false,
                    true, false, false, 0.0, 0.0, depth
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

        // ===== 新增方法实现 =====

        /// <summary>
        /// 绘制圆形
        /// 支持创建圆柱体（圆形 + 旋转）
        /// </summary>
        public bool DrawCircle(double centerX, double centerY, double radius)
        {
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
                    return false;
                }

                // 使用dynamic调用CreateCircle，避免API兼容性问题
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

        /// <summary>
        /// 绘制直线
        /// 支持创建复杂草图
        /// </summary>
        public bool DrawLine(double x1, double y1, double x2, double y2)
        {
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
                    return false;
                }

                // 使用dynamic调用CreateLine
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

        /// <summary>
        /// 创建旋转特征
        /// 用于创建圆柱体、球体等回转体
        /// </summary>
        public bool CreateRevolution(double angle)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 使用dynamic调用FeatureRevolution
                // 参数说明：
                // angle - 旋转角度（弧度）
                //   360度 = 2π ≈ 6.28318 弧度
                //   180度 = π ≈ 3.14159 弧度
                dynamic feature = featureMgr.FeatureRevolution(
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
                    angle,   // angle - 旋转角度（弧度）
                    false,   // reverseDirection
                    0.0      // angle2
                );

                if (feature == null)
                {
                    lastError = "无法创建旋转特征，角度: " + angle;
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建旋转错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 创建圆角特征
        /// 用于边缘圆角处理
        /// </summary>
        public bool CreateFillet(double radius)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 使用dynamic调用FeatureFillet
                // 注意：需要在调用前选择要圆角的边缘
                dynamic feature = featureMgr.FeatureFillet(
                    radius,  // radius - 圆角半径
                    0.0,     // overrideRadius
                    0.0,     // radius2
                    false,   // isPropagate
                    false,   // isTangentPropagate
                    false,   // isCurvatureContinuous
                    0,       // varFilletType
                    0        // options
                );

                if (feature == null)
                {
                    lastError = "无法创建圆角，半径: " + radius;
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建圆角错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 创建倒角特征
        /// 用于边缘倒角处理
        /// </summary>
        public bool CreateChamfer(double distance, double angle)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 使用dynamic调用FeatureChamfer
                // 注意：需要在调用前选择要倒角的边缘
                dynamic feature = featureMgr.FeatureChamfer(
                    1,       // chamferType (1 = angle-distance)
                    distance, // distance
                    angle,   // angle - 倒角角度（度）
                    0.0,     // reverseDistance
                    false,   // keepEdges
                    0        // options
                );

                if (feature == null)
                {
                    lastError = "无法创建倒角，距离: " + distance + ", 角度: " + angle;
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建倒角错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 创建切除特征 - 用于通孔、盲孔等
        /// 关键方法：M5螺母设计必需
        /// </summary>
        public bool CreateCut(double depth)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 使用dynamic调用FeatureCut（切除）
                // 参数与FeatureExtrusion类似，但方向相反（切除材料）
                dynamic feature = featureMgr.FeatureCut(
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
                    depth,   // depth - 切除深度（贯通整个零件）
                    false,   // reverseDirection
                    false,   // useCapPlane
                    0.0      // capPlaneOffset
                );

                if (feature == null)
                {
                    lastError = "无法创建切除特征，深度: " + depth;
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = "创建切除错误: " + ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 创建内螺纹特征 - 用于螺母等
        /// 关键方法：M5螺母设计必需
        /// </summary>
        public bool CreateInternalThread(double diameter, double pitch, double length)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 使用dynamic调用FeatureCutThreading（内螺纹）
                // 这是专门用于创建内螺纹的方法
                dynamic feature = featureMgr.FeatureCutThreading(
                    true,     // directionOne
                    false,    // flipDirection
                    false,    // useDefaultOffset
                    false,    // useFeatureScope
                    false,    // useAutoSelect
                    true,     // maintainTangentChain
                    false,    // isThinFeature
                    false,    // isDraftFeature
                    0.0,      // draftAngle
                    0.0,      // offset
                    length,   // depth - 螺纹长度
                    false,    // reverseDirection
                    false,    // useCapPlane
                    0.0,      // capPlaneOffset
                    diameter, // threadDiameter - 螺纹大径
                    pitch,    // pitch - 螺距
                    0.0,      // minorDiameter - 小径（自动计算）
                    60.0,     // includedAngle - 牙型角（公制螺纹60度）
                    false,    // isMetric - 公制螺纹
                    false,    // isCustom - 非自定义螺纹
                    0,        // clearanceMethod - 间隙方法
                    0.0       // clearance - 间隙值
                );

                if (feature == null)
                {
                    lastError = "无法创建内螺纹，直径: " + diameter + ", 螺距: " + pitch;
                    return false;
                }

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
    }
}
