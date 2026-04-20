// Direct test: Verify "Front Plane" vs "前视基准面"
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

class Test
{
    static void Main()
    {
        Console.WriteLine("SolidWorks Plane Name Test");
        Console.WriteLine("=========================");
        Console.WriteLine();

        SldWorks swApp = new SldWorks();
        ModelDoc2 model = swApp.ActiveDoc;

        if (model == null)
        {
            Console.WriteLine("[ERROR] No active document in SolidWorks");
            Console.WriteLine();
            Console.WriteLine("Please create a part document first:");
            Console.WriteLine("  1. In SolidWorks: File -> New -> Part");
            Console.WriteLine("  2. Run this test again");
            Console.ReadKey();
            return;
        }

        Console.WriteLine("[OK] Found active document");
        Console.WriteLine();

        // Test 1: Chinese name
        Console.WriteLine("Test 1: '前视基准面' (Chinese)");
        object callout1 = Type.Missing;
        try
        {
            bool result1 = model.Extension.SelectByID2("前视基准面", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout1, 0);
            Console.WriteLine("  Result: " + (result1 ? "SUCCESS" : "FAILED"));
        }
        catch (Exception ex)
        {
            Console.WriteLine("  Exception: " + ex.Message);
        }
        Console.WriteLine();

        // Test 2: English name
        Console.WriteLine("Test 2: 'Front Plane' (English)");
        object callout2 = Type.Missing;
        try
        {
            bool result2 = model.Extension.SelectByID2("Front Plane", "PLANE", 0.0, 0.0, 0.0, false, 0, ref callout2, 0);
            Console.WriteLine("  Result: " + (result2 ? "SUCCESS" : "FAILED"));

            if (result2)
            {
                Console.WriteLine();
                Console.WriteLine("=========================");
                Console.WriteLine("[SUCCESS] 'Front Plane' works!");
                Console.WriteLine("=========================");
                Console.WriteLine();
                Console.WriteLine("This confirms the fix is correct.");
                Console.WriteLine("Update SWHelper_Robust.cs and recompile.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("  Exception: " + ex.Message);
        }

        Console.WriteLine();
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }
}
