Sub M24Chamfer()
  Dim swApp As Object: Set swApp = Application.SldWorks
  Dim m As Object: Set m = swApp.ActiveDoc
  Dim fm As Object: Set fm = m.FeatureManager
  Dim i As Long

  Dim vB As Variant: vB = m.GetBodies2(0, False)
  Dim vF As Variant: vF = vB(0).GetFaces
  Dim tF As Object, bF As Object
  For i = 0 To UBound(vF)
    Dim n As Variant: n = vF(i).Normal
    If n(1) > 0.5 Then Set tF = vF(i)
    If n(1) < -0.5 Then Set bF = vF(i)
  Next

  If Not tF Is Nothing Then
    Dim vE As Variant: vE = tF.GetEdges
    m.ClearSelection2 True
    For i = 0 To UBound(vE)
      If i >= 6 Then Exit For
      vE(i).Select4 True, m.SelectionManager.CreateSelectData
    Next
    fm.InsertChamfer 2, 0.0025, 0.5236, False, 0, False
  End If

  If Not bF Is Nothing Then
    Dim vE2 As Variant: vE2 = bF.GetEdges
    m.ClearSelection2 True
    For i = 0 To UBound(vE2)
      If i >= 6 Then Exit For
      vE2(i).Select4 True, m.SelectionManager.CreateSelectData
    Next
    fm.InsertChamfer 2, 0.001, 0.7854, False, 0, False
  End If

  m.ForceRebuild3 True
  MsgBox "Chamfer Done!"
End Sub
