import sys
import pythoncom
pythoncom.CoInitialize()
try:
    import win32com.client
    import win32com.client.dynamic as dynamic

    sw = dynamic.Dispatch("SldWorks.Application")
    print("1. COM connected, SW version:", sw.RevisionNumber)

    part = sw.ActiveDoc
    print("2. Active doc:", part.GetTitle)

    # Use FeatureByName + Select2 instead of SelectByID2 (SW2026 compatible)
    plane_feature = part.FeatureByName("Top Plane")
    if plane_feature:
        selected = plane_feature.Select2(False, 0)
        print("3. Select Top Plane via FeatureByName:", selected)
    else:
        print("3. FeatureByName failed, trying short name")
        plane_feature = part.FeatureByName("Top")
        if plane_feature:
            selected = plane_feature.Select2(False, 0)
            print("3b. Select Top:", selected)

    # Insert sketch
    part.SketchManager.InsertSketch(True)
    print("4. Sketch inserted")

    # Draw hexagon (inscribed R=13.856mm -> across flats 24mm)
    skSeg = part.SketchManager.CreatePolygon(0.0, 0.0, 0.0, 0.013856, 0.0, 0.0, 6, True)
    print("5. Hexagon drawn:", skSeg is not None)

    part.SketchManager.InsertSketch(True)
    print("6. Sketch closed")

    # Select sketch for extrusion - use FeatureByName
    sketch_feature = part.FeatureByName("Sketch1")
    if sketch_feature:
        selected = sketch_feature.Select2(False, 0)
        print("7. Select Sketch1:", selected)
    else:
        print("7. Sketch1 not found by name")

    # Boss extrude 14.8mm
    feat = part.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.0148, 0.0148,
        False, False, False, False,
        0, 0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    print("8. Boss extrude:", feat is not None)
    part.ClearSelection2(True)

    # Rebuild
    part.ForceRebuild3(True)
    print("9. Rebuild complete")
    print("SUCCESS: Modeling operations work with SW2026!")

except Exception as e:
    import traceback
    print("ERROR:", type(e).__name__, str(e))
    traceback.print_exc()
finally:
    pythoncom.CoUninitialize()
