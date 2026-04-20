using System;
using System.Runtime.InteropServices;

namespace SWHelper
{
    /// <summary>
    /// SWHelper接口定义 - 简化演示版
    ///
    /// 注意：这是一个演示版本，用于验证编译和注册流程
    /// 完整版本需要SolidWorks.Interop.sldworks.dll引用
    /// </summary>
    [ComVisible(true)]
    [Guid("2E8F6B3D-4A5E-4B3F-9A2C-1D5F7E8B6A4C")]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelper
    {
        string GetVersion();
        string TestConnect();
        bool DemoMethod();
    }

    /// <summary>
    /// SWHelper实现类 - 简化演示版
    /// </summary>
    [ComVisible(true)]
    [Guid("3F9G7C4E-5B6F-5C4G-0B3D-2E6G8F9C7B5D")]
    [ClassInterface(ClassInterfaceType.None)]
    public class SWHelper : ISWHelper
    {
        private string version = "1.0.0-Demo";

        public string GetVersion()
        {
            return "SWHelper " + version + " - .NET中间层演示版";
        }

        public string TestConnect()
        {
            return "SUCCESS: .NET中间层已正确编译和注册！";
        }

        public bool DemoMethod()
        {
            // 演示方法
            return true;
        }
    }
}
