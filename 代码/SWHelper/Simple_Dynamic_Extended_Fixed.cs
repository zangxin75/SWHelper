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

        // 扩展方法
        bool DrawCircle(double centerX, double centerY, double radius);
        bool DrawLine(double x1, double y1, double x2, double y2);
        bool CreateRevolution(double angle);
        bool CreateFillet(double radius);
        bool CreateChamfer(double distance, double angle);
        bool CreateCut(double depth);
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
        private string version = "1.2-Fixed-Dynamic";
        private string lastError = "";

        public string GetVersion()
        {
            return "SWHelper v" + version + " (Fixed CreatePart)";
        }

        public string TestConnect()
        {
            return "SUCCESS: SWHelper修复版本编译和注册成功！";
        }

        public bool ConnectToSW()
        {
            try
            {
                // 尝试获取运行中的SolidWorks
                try
                {
                    swApp = Marshal.GetActiveObject("SldWorks.Application");
                    if (swApp != null)
                    {
                        lastError = "";
                        return true;
                    }
                }
                catch
                {
                    // 如果没有运行中的实例，创建新的
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

                // 使用默认模板创建零件
                // 不使用GetUserPreferenceStringValue，直接使用空字符串让SolidWorks使用默认模板
                model = swApp.NewDocument("", 0, 0, 0);

                if (model == null)
                {
                    lastError = "无法创建零件 - 可能是模板问题";
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

        // 扩展方法实现
        public bool DrawCircle(double centerX, double centerY, double radius)
        {
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
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
            try
            {
                if (sketchMgr == null)
                {
                    lastError = "草图管理器未初始化";
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

        public bool CreateRevolution(double angle)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                dynamic feature = featureMgr.FeatureRevolution(
                    true, false, false, false, false,
                    true, false, false, 0.0, 0.0, angle,
                    false, 0.0
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

        public bool CreateFillet(double radius)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                dynamic feature = featureMgr.FeatureFillet(
                    radius, 0.0, 0.0, false, false, false, 0, 0
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

        public bool CreateChamfer(double distance, double angle)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                dynamic feature = featureMgr.FeatureChamfer(
                    1, distance, angle, 0.0, false, 0
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

        public bool CreateCut(double depth)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
                    return false;
                }

                dynamic feature = featureMgr.FeatureCut(
                    true, false, false, false, false,
                    true, false, false, 0.0, 0.0, depth,
                    false, false, 0.0
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

        public bool CreateInternalThread(double diameter, double pitch, double length)
        {
            try
            {
                if (featureMgr == null)
                {
                    lastError = "特征管理器未初始化";
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
