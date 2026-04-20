using System;
using System.Reflection;
using SolidWorks.Interop.sldworks;

class Program
{
    static void Main()
    {
        try
        {
            Assembly swAssembly = Assembly.LoadFrom("d:\app_install\solidworks2026\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll");
            
            Console.WriteLine("=== SolidWorks API Analysis ===");
            
            Type modelDocExtType = swAssembly.GetType("SolidWorks.Interop.sldworks.ModelDocExtension");
            if (modelDocExtType != null)
            {
                MethodInfo selectMethod = modelDocExtType.GetMethod("SelectByID2");
                if (selectMethod != null)
                {
                    Console.WriteLine("\nSelectByID2 Method Found:");
                    Console.WriteLine("  Parameters:");
                    ParameterInfo[] params = selectMethod.GetParameters();
                    foreach (ParameterInfo p in params)
                    {
                        Console.WriteLine("    " + p.ParameterType.Name + " " + p.Name);
                    }
                }
            }
            
            Type featMgrType = swAssembly.GetType("SolidWorks.Interop.sldworks.FeatureManager");
            if (featMgrType != null)
            {
                MethodInfo[] methods = featMgrType.GetMethods();
                foreach (MethodInfo m in methods)
                {
                    if (m.Name.StartsWith("FeatureExtrusion"))
                    {
                        Console.WriteLine("\n" + m.Name + " Method Found:");
                        Console.WriteLine("  Parameters: " + m.GetParameters().Length);
                        ParameterInfo[] params = m.GetParameters();
                        foreach (ParameterInfo p in params)
                        {
                            Console.WriteLine("    " + p.ParameterType.Name + " " + p.Name);
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.Message);
        }
    }
}
