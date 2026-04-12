Sub main()
    Dim swApp As Object
    Dim swModel As Object
    Dim swFeatMgr As Object
    Dim myFeature As Object
    
    Set swApp = GetObject(, "SldWorks.Application")
    Set swModel = swApp.ActiveDoc
    
    If swModel Is Nothing Then
        swApp.SendMsgToUser2 "No active document", 0, 0
        Exit Sub
    End If
    
    Set swFeatMgr = swModel.FeatureManager
    
    ' Select the sketch feature first
    Dim swFeat As Object
    Set swFeat = swModel.FeatureByName("Sketch")
    If Not swFeat Is Nothing Then
        swFeat.Select2 False, 0
    End If
    
    ' Boss Extrude: depth = 20mm = 0.02m, blind, merge
    Set myFeature = swFeatMgr.FeatureExtrusion2( _
        True, False, False, 0, 0, _
        0.02, 0.02, _
        False, False, False, False, _
        0, 0, False, False, False, False, _
        True, True, True, 0, 0, False)
    
    If Not myFeature Is Nothing Then
        swApp.SendMsgToUser2 "Base extrusion created: 20mm", 0, 0
    Else
        swApp.SendMsgToUser2 "Extrusion failed", 0, 0
    End If
    
End Sub
