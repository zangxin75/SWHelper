' M24 Nut Finish Macro
Sub M24Finish()
  Dim swApp As Object: Set swApp = Application.SldWorks
  Dim m As Object: Set m = swApp.ActiveDoc
  Dim fm As Object: Set fm = m.FeatureManager
  Dim b As Boolean, i As Long

  ' === Chamfer ===
  Dim vB As Variant: vB = m.GetBodies2(0, False)
  Dim vF As Variant: vF = vB(0).GetFaces
  Dim tF As Object, bF As Object
  For i = 0 To UBound(vF)
    Dim n As Variant: n = vF(i).Normal
    If n(1) > 0.5 Then Set tF = vF(i)
    If n(1) < -0.5 Then Set bF = vF(i)
  Next
  If Not tF Is Nothing Then
    m.ClearSelection2 True
    Dim vE As Variant: vE = tF.GetEdges
    For i = 0 To UBound(vE)
      If i >= 6 Then Exit For
      vE(i).Select4 True, m.SelectionManager.CreateSelectData
    Next
    fm.InsertChamfer 2, 0.0025, 0.5236, False, 0, False
  End If
  If Not bF Is Nothing Then
    m.ClearSelection2 True
    Dim vE2 As Variant: vE2 = bF.GetEdges
    For i = 0 To UBound(vE2)
      If i >= 6 Then Exit For
      vE2(i).Select4 True, m.SelectionManager.CreateSelectData
    Next
    fm.InsertChamfer 2, 0.001, 0.7854, False, 0, False
  End If

  ' === Swept Cut ===
  m.ClearSelection2 True
  b = m.Extension.SelectByID2("ÎeÐýÏß/Ç¢×´Ïß1", "REFERENCECURVES", 0, 0, 0, False, 1, Nothing, 0)
  If Not b Then b = m.Extension.SelectByID2("Helix/Spiral1", "REFERENCECURVES", 0, 0, 0, False, 1, Nothing, 0)
  b = m.Extension.SelectByID2("²ÝÀ§5", "SKETCH", 0, 0, 0, True, 4, Nothing, 0)
  If Not b Then b = m.Extension.SelectByID2("Sketch5", "SKETCH", 0, 0, 0, True, 4, Nothing, 0)
  fm.InsertCutSwept3 False, False, True, 0, False, True, False, 0#, False, 0, 0, 0#, 0#, 0, False

  m.ForceRebuild3 True
  MsgBox "M24 Nut Complete!"
End Sub
