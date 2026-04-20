using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

namespace SWHelper
{
    /// <summary>
    /// SWHelper完整接口定义
    /// 包含100%自动化所需的所有功能
    /// </summary>
    [ComVisible(true)]
    [Guid("2E8F6B3D-4A5E-4B3F-9A2C-1D5F7E8B6A4C")]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelper
    {
        // 连接和初始化
        bool ConnectToSW();
        void SetVisible(bool visible);
        string GetVersion();
        string GetLastError();

        // 文档创建
        bool CreatePart();
        bool CreateAssembly();
        bool CreateDrawing(string templatePath);

        // 草图操作
        bool CreateSketch();
        bool DrawRectangle(double x1, double y1, double x2, double y2);
        bool DrawCircle(double centerX, double centerY, double radius);
        bool DrawLine(double x1, double y1, double x2, double y2);
        bool CloseSketch();

        // 特征操作 - 最后5%功能
        bool SelectSketch(string sketchName);
        bool CreateExtrusion(double depth);
        bool CreateRevolution(double angle);
        bool CreateFillet(double radius);
        bool CreateChamfer(double distance, double angle);
        bool CreateShell(double thickness);

        // 高级功能
        bool SetMaterial(string materialName);
        bool SetUnits(swLengthUnit_e units);
        bool SaveToFile(string filePath);
        bool GetDimensions(out double width, out double height, out double depth);
    }

    /// <summary>
    /// SWHelper完整实现类
    /// 实现100%自动化所需的所有功能
    /// 解决Python COM类型不兼容问题的中间层
    /// </summary>
    [ComVisible(true)]
    [Guid("3F9G7C4E-5B6F-5C4G-0B3D-2E6G8F9C7B5D")]
    [ClassInterface(ClassInterfaceType.None)]
    public class SWHelper : ISWHelper
    {
        private SldWorks swApp;
        private ModelDoc2 model;
        private FeatureManager featureMgr;
        private SketchManager sketchMgr;
        private PartDoc part;
        private string lastError = "";

        #region 连接和初始化

        /// <summary>
        /// 连接到SolidWorks应用程序
        /// </summary>
        public bool ConnectToSW()
        {
            try
            {
                // 尝试连接到已运行的SolidWorks实例
                swApp = (SldWorks)Marshal.GetActiveObject("SldWorks.Application");

                if (swApp != null)
                {
                    lastError = "";
                    return true;
                }

                // 如果没有运行中的实例，创建新实例
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

        /// <summary>
        /// 设置SolidWorks窗口可见性
        /// </summary>
        public void SetVisible(bool visible)
        {
            if (swApp != null)
            {
                swApp.Visible = visible;
            }
        }

        /// <summary>
        /// 获取版本信息
        /// </summary>
        public string GetVersion()
        {
            return "SWHelper v1.0-Full (100% Automation)";
        }

        /// <summary>
        /// 获取最后的错误信息
        /// </summary>
        public string GetLastError()
        {
            return lastError;
        }

        #endregion

        #region 文档创建

        /// <summary>
        /// 创建新的零件文档
        /// </summary>
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

                // 创建新零件文档
                ModelDoc2 newDoc = swApp.NewDocument(
                    swApp.GetUserPreferenceStringValue((int)swUserPreferenceStringValue_e.swDefaultTemplatePart),
                    (int)swDwgPaperSizes_e.swDwgPapersUserDefined,
                    0.0,
                    0.0
                );

                if (newDoc == null)
                {
                    lastError = "无法创建零件文档";
                    return false;
                }

                model = newDoc;
                part = (PartDoc)model;
                featureMgr = model.FeatureManager;
                sketchMgr = model.SketchManager;

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建零件错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 创建新的装配体文档
        /// </summary>
        public bool CreateAssembly()
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

                ModelDoc2 newDoc = swApp.NewDocument(
                    swApp.GetUserPreferenceStringValue((int)swUserPreferenceStringValue_e.swDefaultTemplateAssembly),
                    (int)swDwgPaperSizes_e.swDwgPapersUserDefined,
                    0.0,
                    0.0
                );

                if (newDoc == null)
                {
                    lastError = "无法创建装配体文档";
                    return false;
                }

                model = newDoc;
                featureMgr = model.FeatureManager;
                sketchMgr = model.SketchManager;

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建装配体错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 创建新的工程图文档
        /// </summary>
        public bool CreateDrawing(string templatePath)
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

                ModelDoc2 newDoc = swApp.NewDocument(
                    templatePath,
                    (int)swDwgPaperSizes_e.swDwgPapersUserDefined,
                    0.0,
                    0.0
                );

                if (newDoc == null)
                {
                    lastError = "无法创建工程图文档";
                    return false;
                }

                model = newDoc;
                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建工程图错误: {0}", ex.Message);
                return false;
            }
        }

        #endregion

        #region 草图操作

        /// <summary>
        /// 创建新草图
        /// </summary>
        public bool CreateSketch()
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开的文档";
                    return false;
                }

                // 选择前视基准面
                bool selected = model.Extension.SelectByID2(
                    "前视基准面",
                    "PLANE",
                    0.0,
                    0.0,
                    0.0,
                    false,
                    0,
                    null,
                    0
                );

                if (!selected)
                {
                    lastError = "无法选择前视基准面";
                    return false;
                }

                // 创建草图
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

        /// <summary>
        /// 绘制矩形
        /// </summary>
        public bool DrawRectangle(double x1, double y1, double x2, double y2)
        {
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
                    return false;
                }

                // 绘制矩形（中心点方法）
                double centerX = (x1 + x2) / 2.0;
                double centerY = (y1 + y2) / 2.0;
                double width = Math.Abs(x2 - x1);
                double height = Math.Abs(y2 - y1);

                sketchMgr.CreateCenterRectangle(
                    centerX,
                    centerY,
                    0.0,
                    centerX + width / 2.0,
                    centerY + height / 2.0,
                    0.0
                );

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("绘制矩形错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 绘制圆形
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

                sketchMgr.CreateCircleByRadius(
                    centerX,
                    centerY,
                    0.0,
                    radius
                );

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("绘制圆形错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 绘制直线
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

                sketchMgr.CreateLine(
                    x1,
                    y1,
                    0.0,
                    x2,
                    y2,
                    0.0
                );

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("绘制直线错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 关闭草图
        /// </summary>
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

        #endregion

        #region 特征操作 - 最后5%功能

        /// <summary>
        /// 选择草图 - 解决Python COM类型不兼容问题的关键方法
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

                // 关键：使用正确的参数调用SelectByID2
                // C# 的 ref object callout = null 会正确转换为 COM VARIANT 类型
                object callout = null;
                int selectOption = 0;

                bool selected = model.Extension.SelectByID2(
                    sketchName,
                    "SKETCH",
                    0.0,
                    0.0,
                    0.0,
                    false,
                    0,
                    ref callout,  // 关键！使用 ref 参数传递正确的 VARIANT 类型
                    selectOption
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
        /// 创建拉伸特征 - 最后5%功能之一
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

                // 创建拉伸特征
                Feature feature = featureMgr.FeatureExtrusion2(
                    true,  // directionOne (单向拉伸)
                    false,  // flipDirection
                    false,  // useDefaultOffset
                    false,  // useFeatureScope
                    false,  // useAutoSelect
                    true,   // maintainTangentChain
                    true,   // isThinFeature
                    false,  // isDraftFeature
                    0.0,    // draftAngle
                    0.0,    // offset
                    depth,  // depth (拉伸深度)
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
                    (int)swStartCondition_e.swStartSketchPlane,
                    0.0,
                    (int)swEndCondition_e.swEndCondBlind,
                    0.0,
                    (int)swEndCondition_e.swEndCondBlind,
                    0.0,
                    0.0,
                    false,
                    false
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

        /// <summary>
        /// 创建旋转特征
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

                Feature feature = featureMgr.FeatureRevolve(
                    true,   // directionOne
                    false,  // useDefaultOffset
                    false,  // useFeatureScope
                    false,  // useAutoSelect
                    true,   // maintainTangentChain
                    false,  // isThinFeature
                    false,  // isDraftFeature
                    0.0,    // draftAngle
                    0.0,    // offset
                    angle,  // angle (旋转角度，弧度)
                    0.0,    // angle2
                    false,  // reverseDirection
                    (int)swStartCondition_e.swStartSketchPlane,
                    0.0,
                    (int)swEndCondition_e.swEndCondBlind,
                    0.0,
                    (int)swEndCondition_e.swEndCondBlind,
                    0.0,
                    0.0,
                    true,   // optimize
                    false,
                    false
                );

                if (feature == null)
                {
                    lastError = string.Format("无法创建旋转特征，角度: {0}", angle);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建旋转错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 创建圆角特征
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

                // 创建圆角特征
                object[] radii = new object[1];
                radii[0] = radius;

                Feature feature = featureMgr.FeatureFillet(
                    (int)swFilletFeatureTensorType_e.swFilletFeatureConstantRadius,
                    radii,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null
                );

                if (feature == null)
                {
                    lastError = string.Format("无法创建圆角特征，半径: {0}", radius);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建圆角错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 创建倒角特征
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

                // 创建倒角特征
                Feature feature = featureMgr.FeatureChamfer(
                    (int)swChamferType_e.swChamferAngleDistance,
                    null,
                    distance,
                    angle,
                    null,
                    null,
                    null
                );

                if (feature == null)
                {
                    lastError = string.Format("无法创建倒角特征，距离: {0}, 角度: {1}", distance, angle);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建倒角错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 创建抽壳特征
        /// </summary>
        public bool CreateShell(double thickness)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                // 创建抽壳特征
                Feature feature = featureMgr.FeatureShell(
                    thickness,
                    null,
                    false,
                    false,
                    false,
                    false,
                    false
                );

                if (feature == null)
                {
                    lastError = string.Format("无法创建抽壳特征，厚度: {0}", thickness);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("创建抽壳错误: {0}", ex.Message);
                return false;
            }
        }

        #endregion

        #region 高级功能

        /// <summary>
        /// 设置材料
        /// </summary>
        public bool SetMaterial(string materialName)
        {
            try
            {
                if (part == null)
                {
                    lastError = "零件文档未初始化";
                    return false;
                }

                bool result = part.SetMaterialPropertyName(
                    materialName,
                    "",
                    ""
                );

                if (!result)
                {
                    lastError = string.Format("无法设置材料: {0}", materialName);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("设置材料错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 设置单位
        /// </summary>
        public bool SetUnits(swLengthUnit_e units)
        {
            try
            {
                if (model == null)
                {
                    lastError = "文档未初始化";
                    return false;
                }

                bool result = model.SetUnits(
                    (int)units,
                    (int)swLengthUnitFractionsOrDecimals_e.swLengthUnitDecimals,
                    2,
                    false,
                    (int)swAngularUnit_e.swAngularUnitRadians,
                    0,
                    false
                );

                if (!result)
                {
                    lastError = string.Format("无法设置单位: {0}", units);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("设置单位错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 保存到文件
        /// </summary>
        public bool SaveToFile(string filePath)
        {
            try
            {
                if (model == null)
                {
                    lastError = "没有打开的文档";
                    return false;
                }

                int saveResult = model.SaveToFile(filePath);

                if (saveResult != 0)
                {
                    lastError = string.Format("无法保存文件: {0}", filePath);
                    return false;
                }

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("保存文件错误: {0}", ex.Message);
                return false;
            }
        }

        /// <summary>
        /// 获取零件尺寸
        /// </summary>
        public bool GetDimensions(out double width, out double height, out double depth)
        {
            width = 0.0;
            height = 0.0;
            depth = 0.0;

            try
            {
                if (model == null)
                {
                    lastError = "没有打开的文档";
                    return false;
                }

                // 获取边界框
                double[] bbox = (double[])model.GetBox(false);

                if (bbox == null || bbox.Length < 6)
                {
                    lastError = "无法获取零件尺寸";
                    return false;
                }

                width = Math.Abs(bbox[3] - bbox[0]);
                height = Math.Abs(bbox[4] - bbox[1]);
                depth = Math.Abs(bbox[5] - bbox[2]);

                lastError = "";
                return true;
            }
            catch (Exception ex)
            {
                lastError = string.Format("获取尺寸错误: {0}", ex.Message);
                return false;
            }
        }

        #endregion
    }
}
