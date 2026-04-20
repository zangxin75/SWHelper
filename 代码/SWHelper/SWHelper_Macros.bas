Attribute VB_Name = "SWHelperMacros"
Option Explicit

'===========================================================
' SWHelper VBA宏模块 - 用于SolidWorks 2026
' 创建日期: 2026-04-14
' 版本: 1.0
'===========================================================

'-----------------------------------------------------------
' 创建草图 - 在前视基准面上
'-----------------------------------------------------------
Sub CreateSketchOnFrontPlane()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    ' 获取SolidWorks应用
    Set swApp = Application.SldWorks

    ' 检查是否有活动文档
    Set Model = swApp.ActiveDoc
    If Model Is Nothing Then
        Err.Raise vbObjectError + 1, "CreateSketch", "没有活动文档"
    End If

    ' 选择前视基准面
    boolstatus = Model.Extension.SelectByID2("Front Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If Not boolstatus Then
        Err.Raise vbObjectError + 2, "CreateSketch", "基准面选择失败"
    End If

    ' 插入草图
    boolstatus = Model.SketchManager.InsertSketch(True)

    If Not boolstatus Then
        Err.Raise vbObjectError + 3, "CreateSketch", "草图插入失败"
    End If

    ' 成功
    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "CreateSketch"
End Sub

'-----------------------------------------------------------
' 创建草图 - 在上视基准面上
'-----------------------------------------------------------
Sub CreateSketchOnTopPlane()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    Set swApp = Application.SldWorks
    Set Model = swApp.ActiveDoc

    If Model Is Nothing Then
        Err.Raise vbObjectError + 1, "CreateSketch", "没有活动文档"
    End If

    boolstatus = Model.Extension.SelectByID2("Top Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If Not boolstatus Then
        Err.Raise vbObjectError + 2, "CreateSketch", "基准面选择失败"
    End If

    boolstatus = Model.SketchManager.InsertSketch(True)

    If Not boolstatus Then
        Err.Raise vbObjectError + 3, "CreateSketch", "草图插入失败"
    End If

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "CreateSketch"
End Sub

'-----------------------------------------------------------
' 创建草图 - 在右视基准面上
'-----------------------------------------------------------
Sub CreateSketchOnRightPlane()
    Dim swApp As Object
    Dim Model As Object
    Dim boolstatus As Boolean

    On Error GoTo ErrorHandler

    Set swApp = Application.SldWorks
    Set Model = swApp.ActiveDoc

    If Model Is Nothing Then
        Err.Raise vbObjectError + 1, "CreateSketch", "没有活动文档"
    End If

    boolstatus = Model.Extension.SelectByID2("Right Plane", "PLANE", 0#, 0#, 0#, False, 0, Nothing, 0)

    If Not boolstatus Then
        Err.Raise vbObjectError + 2, "CreateSketch", "基准面选择失败"
    End If

    boolstatus = Model.SketchManager.InsertSketch(True)

    If Not boolstatus Then
        Err.Raise vbObjectError + 3, "CreateSketch", "草图插入失败"
    End If

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "CreateSketch"
End Sub

'-----------------------------------------------------------
' 创建零件文档
'-----------------------------------------------------------
Sub CreateNewPart()
    Dim swApp As Object
    Dim Model As Object

    On Error GoTo ErrorHandler

    Set swApp = Application.SldWorks
    Set Model = swApp.NewDocument("", 1, 0, 0)

    If Model Is Nothing Then
        Err.Raise vbObjectError + 1, "CreatePart", "无法创建零件文档"
    End If

    Exit Sub

ErrorHandler:
    MsgBox "错误: " & Err.Description, vbCritical, "CreatePart"
End Sub

'-----------------------------------------------------------
' 关闭草图
'-----------------------------------------------------------
Sub CloseSketch()
    Dim swApp As Object
    Dim Model As Object

    On Error Resume Next

    Set swApp = Application.SldWorks
    Set Model = swApp.ActiveDoc

    If Not Model Is Nothing Then
        Model.SketchManager.InsertSketch True
    End If
End Sub
