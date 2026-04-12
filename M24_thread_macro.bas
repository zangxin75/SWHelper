' M24x3 Thread Complete Macro
Sub CreateM24Thread()
  Dim swApp As Object: Set swApp = Application.SldWorks
  Dim swModel As Object: Set swModel = swApp.ActiveDoc
  Dim swFM As Object: Set swFM = swModel.FeatureManager
  Dim b As Boolean

  ' Select Helix/Spiral1
  b = swModel.Extension.SelectByID2("Helix/Spiral1", "REFERENCECURVES", 0, 0, 0, False, 1, Nothing, 0)
  If Not b Then
    b = swModel.Extension.SelectByID2("ÎeÐýÏß/Ç¢×´Ïß1", "REFERENCECURVES", 0, 0, 0, False, 1, Nothing, 0)
  End If

  ' Select last sketch (thread profile)
  Dim featCount As Long: featCount = swModel.GetFeatureCount
  b = swModel.Extension.SelectByID2("Sketch" & featCount, "SKETCH", 0, 0, 0, True, 4, Nothing, 0)

  ' Swept cut
  swFM.InsertCutSwept3 False, False, True, 0, False, True, False, 0, False, False, False, 0.001, 0.001, 0, False
  MsgBox "Thread done!"
End Sub
