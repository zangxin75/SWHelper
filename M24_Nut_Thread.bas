Option Explicit
Sub M24NutThread()
  Dim swApp As SldWorks.SldWorks
  Dim m As SldWorks.ModelDoc2
  Dim fm As SldWorks.FeatureManager
  Dim sm As SldWorks.SelectionMgr
  Dim sk As SldWorks.SketchManager

  Set swApp = Application.SldWorks
  Set m = swApp.ActiveDoc
  If m Is Nothing Then Exit Sub
  Set fm = m.FeatureManager
  Set sm = m.SelectionManager
  Set sk = m.SketchManager

  Dim b As Boolean
  Dim i As Long

  ' ========== 1. Create Helix ==========
  ' Select the circle sketch on Top Plane (should be the last sketch before this macro runs)
  ' Find the sketch by iterating features
  Dim fts As Variant
  Dim skName As String
  fts = fm.GetFeatures(False)

  ' Find the circle sketch (not 草图1 or 草图2)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "ProfileFeature" Then
      If InStr(fts(i).Name, "草图1") = 0 And InStr(fts(i).Name, "草图2") = 0 Then
        skName = fts(i).Name
      End If
    End If
  Next

  If skName = "" Then
    ' Create circle on Top Plane
    m.ClearSelection2 True
    m.Extension.SelectByID2 "上视基准面", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    m.InsertSketch2 True
    sk.CreateCircle 0, 0, 0, 0.010375, 0, 0
    m.InsertSketch2 True

    ' Find the new sketch name
    fts = fm.GetFeatures(False)
    For i = 0 To UBound(fts)
      If fts(i).GetTypeName = "ProfileFeature" Then
        If InStr(fts(i).Name, "草图1") = 0 And InStr(fts(i).Name, "草图2") = 0 Then
          skName = fts(i).Name
        End If
      End If
    Next
  End If

  ' Select the circle sketch and create helix
  m.ClearSelection2 True
  m.Extension.SelectByID2 skName, "SKETCH", 0, 0, 0, False, 0, Nothing, 0

  Dim pitch As Double: pitch = 0.003       ' 3mm
  Dim nutH As Double: nutH = 0.019         ' 19mm

  ' InsertHelix(revDir, taperOut, taperAng, isH, h, p, cw, startAng)
  fm.InsertHelix False, False, 0#, True, nutH, pitch, True, 0#

  ' ========== 2. Thread Profile Sketch ==========
  ' Create on Front Plane at Y=0 (where helix starts)
  m.ClearSelection2 True
  m.Extension.SelectByID2 "前视基准面", "PLANE", 0, 0, 0, False, 0, Nothing, 0
  m.InsertSketch2 True

  Dim hr As Double: hr = 0.010375   ' hole radius
  Dim td As Double: td = 0.001625   ' thread depth
  Dim hp As Double: hp = 0.0015     ' half pitch

  sk.CreateLine hr, 0, 0, hr + td, 0, 0
  sk.CreateLine hr + td, 0, 0, hr + td / 2, hp, 0
  sk.CreateLine hr + td / 2, hp, 0, hr, 0, 0

  m.InsertSketch2 True

  ' Find the profile sketch
  Dim profName As String
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "ProfileFeature" Then
      profName = fts(i).Name
    End If
  Next

  ' ========== 3. Swept Cut ==========
  ' Find helix name
  Dim helixName As String
  fts = fm.GetFeatures(False)
  For i = 0 To UBound(fts)
    If fts(i).GetTypeName = "Helix" Then
      helixName = fts(i).Name
    End If
  Next

  m.ClearSelection2 True
  ' Select helix as path (mark=1)
  m.Extension.SelectByID2 helixName, "REFERENCECURVES", 0, 0, 0, False, 1, Nothing, 0
  ' Select profile sketch (mark=4)
  m.Extension.SelectByID2 profName, "SKETCH", 0, 0, 0, True, 4, Nothing, 0

  ' InsertCutSwept3
  fm.InsertCutSwept3 False, False, True, 0, False, True, False, 0#, False, 0, 0, 0#, 0#, 0, False

  ' ========== 4. Chamfer ==========
  Dim vBodies As Variant: vBodies = m.GetBodies2(swSolidBody, False)
  Dim vFaces As Variant: vFaces = vBodies(0).GetFaces
  Dim topFace As SldWorks.Face2
  Dim botFace As SldWorks.Face2

  For i = 0 To UBound(vFaces)
    Dim nv As Variant: nv = vFaces(i).Normal
    If nv(1) > 0.5 Then Set topFace = vFaces(i)
    If nv(1) < -0.5 Then Set botFace = vFaces(i)
  Next

  ' Top chamfer: 2.5mm x 30deg
  If Not topFace Is Nothing Then
    m.ClearSelection2 True
    Dim vEdges As Variant: vEdges = topFace.GetEdges
    Dim j As Long
    For j = 0 To UBound(vEdges)
      If j >= 6 Then Exit For
      vEdges(j).Select4 True, sm.CreateSelectData
    Next
    fm.InsertChamfer swChamferAngleDist, 0.0025, 30 * 3.14159265 / 180, False, 0, False
  End If

  ' Bottom chamfer: 1mm x 45deg
  If Not botFace Is Nothing Then
    Dim vEdges2 As Variant: vEdges2 = botFace.GetEdges
    m.ClearSelection2 True
    For j = 0 To UBound(vEdges2)
      If j >= 6 Then Exit For
      vEdges2(j).Select4 True, sm.CreateSelectData
    Next
    fm.InsertChamfer swChamferAngleDist, 0.001, 45 * 3.14159265 / 180, False, 0, False
  End If

  ' ========== 5. Save ==========
  m.ForceRebuild3 True
  m.SaveAs2 "C:\Users\Public\Documents\M24_Nut_Complete.sldprt", 0, True, True

  MsgBox "M24 Nut with Thread Complete!", vbInformation
End Sub