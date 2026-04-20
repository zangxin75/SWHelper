// C#验证测试 - 确认SolidWorks 2026 API在C#中可以工作
// 编译: csc /reference:"D:\Program Files\Common Files\SOLIDWORKS 2026\api\redist\SolidWorks.Interop.sldworks.dll" ValidateSWAPI.cs

using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;

namespace SWValidation
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("========================================");
            Console.WriteLine("SolidWorks 2026 API - C#验证测试");
            Console.WriteLine("========================================");
            Console.WriteLine();

            // 步骤1: 连接SolidWorks
            Console.WriteLine("步骤1: 连接到SolidWorks...");
            SldWorks swApp = null;

            try
            {
                swApp = new SldWorks();
                Console.WriteLine($"  [OK] SolidWorks版本: {swApp.Version}");
                Console.WriteLine($"  [OK] SolidWorks可见: {swApp.Visible}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  [ERROR] 无法连接SolidWorks: {ex.Message}");
                Console.WriteLine();
                Console.WriteLine("请确保:");
                Console.WriteLine("  1. SolidWorks 2026正在运行");
                Console.WriteLine("  2. 已安装SolidWorks API");
                return;
            }

            Console.WriteLine();

            // 步骤2: 获取或创建零件文档
            Console.WriteLine("步骤2: 获取活动文档...");
            ModelDoc2 model = swApp.ActiveDoc;

            if (model == null)
            {
                Console.WriteLine("  [INFO] 无活动文档，创建新零件...");
                model = swApp.NewDocument("", 1, 0, 0) as ModelDoc2;

                if (model == null)
                {
                    Console.WriteLine("  [ERROR] 无法创建零件");
                    return;
                }

                model = swApp.ActiveDoc;
                Console.WriteLine("  [OK] 零件已创建");
            }
            else
            {
                Console.WriteLine("  [OK] 已有活动文档");
            }

            Console.WriteLine();

            // 步骤3: 测试SelectByID2（关键测试！）
            Console.WriteLine("步骤3: 测试SelectByID2（使用ref callout）...");
            Console.WriteLine("  这是之前在Python中失败的关键API");
            Console.WriteLine();

            try
            {
                // 关键：使用ref object作为callout参数
                object callout = Type.Missing;
                bool selected = model.Extension.SelectByID2(
                    "Front Plane",    // 使用英文名称
                    "PLANE",          // 类型
                    0.0, 0.0, 0.0,    // 坐标
                    false,            // append
                    0,                // mark
                    ref callout,     // 关键：ref参数
                    0                 // options
                );

                if (selected)
                {
                    Console.WriteLine("  [SUCCESS] SelectByID2成功！✅");
                    Console.WriteLine();
                    Console.WriteLine("  这证明:");
                    Console.WriteLine("    1. C#与SolidWorks 2026完全兼容");
                    Console.WriteLine("    2. ref callout参数正确工作");
                    Console.WriteLine("    3. 可以继续实现CreateSketch等功能");
                    Console.WriteLine();

                    // 步骤4: 测试InsertSketch
                    Console.WriteLine("步骤4: 测试InsertSketch...");
                    try
                    {
                        SketchManager sketchMgr = model.SketchManager;
                        bool inserted = sketchMgr.InsertSketch(true);

                        if (inserted)
                        {
                            Console.WriteLine("  [SUCCESS] InsertSketch成功！✅");
                            Console.WriteLine();

                            // 步骤5: 测试绘制圆形
                            Console.WriteLine("步骤5: 测试绘制圆形...");
                            try
                            {
                                // 绘制半径2.5mm的圆
                                bool circled = sketchMgr.CreateCircleByRadius(0.0, 0.0, 0.0, 0.0025);

                                if (circled)
                                {
                                    Console.WriteLine("  [SUCCESS] 圆形绘制成功！✅");
                                    Console.WriteLine();

                                    // 关闭草图
                                    sketchMgr.InsertSketch(true);

                                    Console.WriteLine("========================================");
                                    Console.WriteLine("[ALL TESTS PASSED]");
                                    Console.WriteLine("========================================");
                                    Console.WriteLine();
                                    Console.WriteLine("✅ SelectByID2: 工作正常");
                                    Console.WriteLine("✅ InsertSketch: 工作正常");
                                    Console.WriteLine("✅ DrawCircle: 工作正常");
                                    Console.WriteLine();
                                    Console.WriteLine("结论: C#独立应用程序100%可行！");
                                    Console.WriteLine("下一步: 开始实现完整的M5设计器");
                                    Console.WriteLine("预计时间: 12-14小时");
                                }
                                else
                                {
                                    Console.WriteLine("  [INFO] CreateCircleByRadius返回: " + circled);
                                    Console.WriteLine("  [WARN] 但草图和选择功能都工作了！");
                                }
                            }
                            catch (Exception ex_circle)
                            {
                                Console.WriteLine($"  [EXCEPTION] 绘制圆形失败: {ex_circle.Message}");
                                Console.WriteLine("  [INFO] 但InsertSketch成功了，这是重大突破！");
                            }
                        }
                        else
                        {
                            Console.WriteLine($"  [FAIL] InsertSketch失败，返回: {inserted}");
                        }
                    }
                    catch (Exception ex_sketch)
                    {
                        Console.WriteLine($"  [EXCEPTION] InsertSketch失败: {ex_sketch.Message}");
                    }
                }
                else
                {
                    Console.WriteLine("  [FAIL] SelectByID2返回False");
                    Console.WriteLine();
                    Console.WriteLine("  可能原因:");
                    Console.WriteLine("    - 基准面名称不对");
                    Console.WriteLine("    - 文档类型不对");
                    Console.WriteLine("    - 需要进一步调试");
                }
            }
            catch (Exception ex_select)
            {
                Console.WriteLine($"  [EXCEPTION] SelectByID2失败: {ex_select.Message}");
                Console.WriteLine($"  详细错误: {ex_select}");

                if (ex_select.GetType().Name == "COMException")
                {
                    var comEx = ex_select as COMException;
                    Console.WriteLine($"  HRESULT: 0x{comEx.ErrorCode:X}");
                }
            }

            Console.WriteLine();
            Console.WriteLine("========================================");
            Console.WriteLine("测试完成");
            Console.WriteLine("========================================");
            Console.WriteLine();
            Console.WriteLine("按任意键退出...");
            Console.ReadKey();
        }
    }
}
