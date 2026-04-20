Attribute VB_Name = "QuickTest"
Option Explicit

' 快速验证VBA宏
' 在SolidWorks中运行此宏来验证CreateSketch是否可以工作

Sub TestCreateSketch()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    ' 获取SolidWorks应用
    Set swApp = Application.SldWorks

    ' 检查是否有活动文档
    Set Model = swApp.ActiveDoc
    If Model Is Nothing Then
        MsgBox "错误：没有活动文档。请先创建一个零件文档。", vbCritical
        Exit Sub
    End If

    ' 尝试创建草图
    MsgBox "开始测试CreateSketch...", vbInformation

    ' 选择前视基准面
    boolstatus = Model.Extension.SelectByID2("Front Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If boolstatus Then
        MsgBox "步骤1：基准面选择成功！"

        ' 插入草图
        boolstatus = Model.SketchManager.InsertSketch(True)

        If boolstatus Then
            MsgBox "✓ SUCCESS: CreateSketch完全成功！", vbInformation, "测试结果"
            MsgBox "这证明VBA可以用于SolidWorks 2026自动化。", vbInformation
        Else
            MsgBox "✗ FAIL: InsertSketch失败", vbCritical, "测试结果"
        End If
    Else
        MsgBox "✗ FAIL: 基准面选择失败", vbCritical, "测试结果"
        MsgBox "可能原因：" & vbCrLf & _
               "1. 基准面名称不对" & vbCrLf & _
               "2. 文档状态有问题", vbInformation
    End If

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description & vbCrLf & vbCrLf & _
           "错误号: " & Err.Number, vbCritical, "测试失败"
End Sub
