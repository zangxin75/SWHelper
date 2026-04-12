Option Explicit
Sub M24NutComplete()
  Dim swApp As SldWorks.SldWorks
  Dim m As SldWorks.ModelDoc2
  Dim fm As SldWorks.FeatureManager
  Dim sk As SldWorks.SketchManager
  Dim ext As SldWorks.ModelDocExtension
  Dim sm As SldWorks.SelectionMgr

  Set swApp = Application.SldWorks
  Set m = swApp.ActiveDoc
  If m Is Nothing Then Exit Sub
  Set fm = m.FeatureManager
  Set sk = m.SketchManager
  Set ext = m.Extension
  Set sm = m.SelectionManager

  Dim b As Boolean
  Dim i As Long, j As Long

  ' ========== Cleanup (keep hex body + hole) ==========
  Dim fts As Variant
  Dim fn As String
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    fn = fts(i).Name
    If InStr(fn, "螺旋") > 0 Or InStr(fn, "Helix") > 0 Or _
       InStr(fn, "曲线") > 0 Or InStr(fn, "扫描") > 0 Or _
       InStr(fn, "切除") > 0 Or InStr(fn, "倒角") > 0 Or _
       InStr(fn, "Chamfer") > 0 Then
      m.ClearSelection2 True
      fts(i).Select2 False, 0
      m.DeleteSelection2 0
    End If
  Next

  ' Delete extra sketches
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "ProfileFeature" Then
      fn = fts(i).Name
      If InStr(fn, "草图1") = 0 And InStr(fn, "草图2") = 0 Then
        m.ClearSelection2 True
        fts(i).Select2 False, 0
        m.DeleteSelection2 0
      End If
    End If
  Next
  m.ForceRebuild3 True

  ' ========== Circle on Top Plane ==========
  m.ClearSelection2 True
  b = ext.SelectByID2("上视基准面", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
  m.InsertSketch2 True
  m.SetAddToDB True
  m.ClearSelection2 True
  sk.CreateCircle 0, 0, 0, 0.010375, 0, 0
  m.SetAddToDB False
  m.InsertSketch2 True

  ' ========== Helix ==========
  Dim skCircleName As String
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "ProfileFeature" Then
      If InStr(fts(i).Name, "草图1") = 0 And InStr(fts(i).Name, "草图2") = 0 Then
        skCircleName = fts(i).Name
      End If
    End If
  Next

  m.ClearSelection2 True
  b = ext.SelectByID2(skCircleName, "SKETCH", 0, 0, 0, True, 0, Nothing, 0)
  m.InsertHelix False, False, 0#, True, 0.019, 0.003, True, 0#, 0#, False
  m.ForceRebuild3 True

  ' Find helix name
  Dim helixName As String
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "Helix" Then
      helixName = fts(i).Name
    End If
  Next

  ' ========== Thread profile on Front Plane ==========
  m.ClearSelection2 True
  b = ext.SelectByID2("前视基准面", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
  m.InsertSketch2 True
  m.SetAddToDB True
  m.ClearSelection2 True

  sk.CreateLine 0.010375, 0, 0, 0.012, 0, 0
  sk.CreateLine 0.012, 0, 0, 0.0111875, 0.0015, 0
  sk.CreateLine 0.0111875, 0.0015, 0, 0.010375, 0, 0

  m.SetAddToDB False
  m.InsertSketch2 True

  ' Find profile sketch
  Dim profName As String
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "ProfileFeature" Then
      If InStr(fts(i).Name, "草图1") = 0 And InStr(fts(i).Name, "草图2") = 0 Then
        profName = fts(i).Name
      End If
    End If
  Next

  ' ========== Swept Cut ==========
  m.ClearSelection2 True
  b = ext.SelectByID2(helixName, "REFERENCECURVES", 0, 0, 0, False, 1, Nothing, 0)
  b = ext.SelectByID2(profName, "SKETCH", 0, 0, 0, True, 4, Nothing, 0)
  fm.InsertCutSwept3 False, False, False, 0, False, True, False, 0#, False, 0, 0, 0#, 0#, 0, False
  m.ForceRebuild3 True

  ' ========== Chamfer ==========
  Dim vBodies As Variant: vBodies = m.GetBodies2(swSolidBody, False)
  Dim vFaces As Variant: vFaces = vBodies(0).GetFaces
  Dim tF As Object, bF As Object
  For i = 0 To UBound(vFaces)
    Dim nv As Variant: nv = vFaces(i).Normal
    If nv(1) > 0.5 Then Set tF = vFaces(i)
    If nv(1) < -0.5 Then Set bF = vFaces(i)
  Next

  If Not tF Is Nothing Then
    m.ClearSelection2 True
    Dim vE As Variant: vE = tF.GetEdges
    For j = 0 To UBound(vE)
      If j >= 6 Then Exit For
      vE(j).Select4 True, sm.CreateSelectData
    Next
    fm.InsertChamfer swChamferAngleDist, 0.0025, 30 * 3.14159265 / 180, False, 0, False
  End If

  If Not bF Is Nothing Then
    m.ClearSelection2 True
    Dim vE2 As Variant: vE2 = bF.GetEdges
    For j = 0 To UBound(vE2)
      If j >= 6 Then Exit For
      vE2(j).Select4 True, sm.CreateSelectData
    Next
    fm.InsertChamfer swChamferAngleDist, 0.001, 45 * 3.14159265 / 180, False, 0, False
  End If

  m.ForceRebuild3 True
  m.SaveAs2 "C:\Users\Public\Documents\M24_Nut_Complete.sldprt", 0, True, True
  Debug.Print "===== M24 Nut Complete! ====="
End Sub