Attribute VB_Name = "CompleteAutomation"
Option Explicit

' ==============================================
' SWHelper V14.5 - 95% 自动化方案
' CreatePart: 自动化 (C# COM)
' CreateSketch: 半自动 (VBA宏)
' ==============================================

Sub TestCreateSketch()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    Set swApp = Application.SldWorks
    Set Model = swApp.ActiveDoc

    If Model Is Nothing Then
        MsgBox "请先运行Python脚本创建零件" & vbCrLf & _
               "cd D:\sw2026\代码\测试代码" & vbCrLf & _
               "py test_create_part_only.py", vbExclamation, "提示"
        Exit Sub
    End If

    ' 创建草图（前视基准面）
    boolstatus = Model.Extension.SelectByID2("Front Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If boolstatus Then
        Model.SketchManager.InsertSketch True
        MsgBox "✅ 草图创建成功！" & vbCrLf & vbCrLf & _
               "现在可以绘制几何图形了", vbInformation, "成功"
    Else
        MsgBox "❌ 选择基准面失败", vbCritical, "失败"
    End If

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "错误"
End Sub

Sub CreateM5Bolt()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    Set swApp = Application.SldWorks
    Set Model = swApp.ActiveDoc

    If Model Is Nothing Then
        MsgBox "请先创建零件", vbExclamation, "提示"
        Exit Sub
    End If

    ' 步骤1：创建草图
    boolstatus = Model.Extension.SelectByID2("Front Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If Not boolstatus Then
        MsgBox "无法选择基准面", vbCritical, "失败"
        Exit Sub
    End If

    Model.SketchManager.InsertSketch True

    ' 步骤2：绘制M5螺栓圆形（直径5mm，半径2.5mm）
    Model.SketchManager.CreateCircle(0#, 0#, 0#, 0.0025#, 0#, 0#)

    ' 步骤3：关闭草图
    Model.SketchManager.InsertSketch False

    ' 步骤4：创建拉伸特征（深度10mm）
    Dim FeatureManager As Object
    Set FeatureManager = Model.FeatureManager

    FeatureManager.FeatureExtrusion2 True, False, False, False, False, False, False, False, False, False, _
        0.01, 0, False, False, False, False, 0.01, 0, False, False, False, False, False, True

    MsgBox "✅ M5螺栓主体创建成功！" & vbCrLf & vbCrLf & _
           "直径: 5mm" & vbCrLf & _
           "长度: 10mm" & vbCrLf & vbCrLf & _
           "后续步骤：" & vbCrLf & _
           "- 手动添加螺纹特征", vbInformation, "成功"

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "错误"
End Sub

Sub CreateM5Nut()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    Set swApp = Application.SldWorks
    Set Model = swApp.ActiveDoc

    If Model Is Nothing Then
        MsgBox "请先创建零件", vbExclamation, "提示"
        Exit Sub
    End If

    ' 步骤1：创建草图
    boolstatus = Model.Extension.SelectByID2("Front Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If Not boolstatus Then
        MsgBox "无法选择基准面", vbCritical, "失败"
        Exit Sub
    End If

    Model.SketchManager.InsertSketch True

    ' 步骤2：绘制M5螺母外圆（直径8mm，半径4mm）
    Model.SketchManager.CreateCircle(0#, 0#, 0#, 0.004#, 0#, 0#)

    ' 步骤3：绘制内孔（直径5mm，半径2.5mm）
    Model.SketchManager.CreateCircle(0#, 0#, 0#, 0.0025#, 0#, 0#)

    ' 步骤4：关闭草图
    Model.SketchManager.InsertSketch False

    ' 步骤5：创建拉伸特征（深度4mm）
    Dim FeatureManager As Object
    Set FeatureManager = Model.FeatureManager

    FeatureManager.FeatureExtrusion2 True, False, False, False, False, False, False, False, False, False, _
        0.004, 0, False, False, False, False, 0.004, 0, False, False, False, False, False, True

    MsgBox "✅ M5螺母主体创建成功！" & vbCrLf & vbCrLf & _
           "外径: 8mm" & vbCrLf & _
           "内径: 5mm" & vbCrLf & _
           "厚度: 4mm" & vbCrLf & vbCrLf & _
           "后续步骤：" & vbCrLf & _
           "- 手动添加螺纹特征", vbInformation, "成功"

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "错误"
End Sub
