using System;
using System.Runtime.InteropServices;

namespace SWHelper
{
    [ComVisible(true)]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface ISWHelper
    {
        string GetVersion();
        string TestConnect();
        bool DemoMethod();
    }

    [ComVisible(true)]
    [ClassInterface(ClassInterfaceType.None)]
    public class SWHelper : ISWHelper
    {
        private string version = "1.0-Demo";

        public string GetVersion()
        {
            return "SWHelper v" + version;
        }

        public string TestConnect()
        {
            return "SUCCESS: SWHelper编译和注册成功！";
        }

        public bool DemoMethod()
        {
            return true;
        }
    }
}
