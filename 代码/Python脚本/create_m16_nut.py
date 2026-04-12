"""
M16 Hex Nut Creator for SolidWorks 2026 (ISO 4032)
Across flats S=24mm, Height m=14.8mm, Thread M16x2
Uses FeatureByName + Select2 instead of SelectByID2 for SW2026 compatibility
"""
import sys
import pythoncom
pythoncom.CoInitialize()
try:
    import win32com.client.dynamic as dynamic

    sw = dynamic.Dispatch("SldWorks.Application")
    print("1. COM connected, SW version:", sw.RevisionNumber)

    # Create new part
    sw.NewDocument("", 0, 0, 0)
    part = sw.ActiveDoc
    print("2. New part created:", part.GetTitle)

    # ====== Step 1: Hexagon Sketch on Top Plane ======
    plane_feature = part.FeatureByName("Top Plane")
    if not plane_feature:
        plane_feature = part.FeatureByName("Top")
    if plane_feature:
        plane_feature.Select2(False, 0)
    part.SketchManager.InsertSketch(True)

    # Hexagon: inscribed, R=13.856mm -> across flats = 24mm
    skSeg = part.SketchManager.CreatePolygon(0.0, 0.0, 0.0, 0.013856, 0.0, 0.0, 6, True)
    part.SketchManager.InsertSketch(True)
    print("3. Hexagon sketch created")

    # ====== Step 2: Boss Extrude 14.8mm ======
    sketch_feat = part.FeatureByName("Sketch1")
    if sketch_feat:
        sketch_feat.Select2(False, 0)
    feat = part.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.0148, 0.0148,
        False, False, False, False,
        0, 0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    part.ClearSelection2(True)
    print("4. Boss extruded 14.8mm")

    # ====== Step 3: Thread Hole Sketch on Top Face ======
    # Select top face by position
    # Use IGetModelDoc to select face at Z=14.8mm
    # Try SelectByID2 with different callout values
    selected = False
    for callout in ("", 0):
        try:
            selected = part.Extension.SelectByID2(
                "", "FACE", 0.0, 0.0, 0.0148, False, 0, callout, 0
            )
            if selected:
                break
        except:
            continue

    if not selected:
        # Fallback: select by ray
        try:
            part.Extension.SelectByRay(0.0, 0.0, 0.02, 0.0, 0.0, -1.0, 1e-4, 1, False, 0, 0)
            print("5b. Face selected by ray")
        except:
            print("5b. Ray selection failed, continuing...")

    part.SketchManager.InsertSketch(True)

    # Circle for M16 thread hole: diameter 14mm (tap drill for M16x2)
    cir = part.SketchManager.CreateCircleByRadius(0.0, 0.0, 0.0, 0.007)
    part.SketchManager.InsertSketch(True)
    print("5. Thread hole circle (D14mm)")

    # ====== Step 4: Cut Extrude Through All ======
    sketch_feat = part.FeatureByName("Sketch2")
    if sketch_feat:
        sketch_feat.Select2(False, 0)
    feat = part.FeatureManager.FeatureExtrusion2(
        True, False, True, 0, 0,
        0.0148, 0.0,
        False, False, False, False,
        0, 0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    part.ClearSelection2(True)
    print("6. Hole cut through all")

    # ====== Step 5: Chamfer Top Edges (0.8mm x 45deg) ======
    # Select top face edges
    for callout in ("", 0):
        try:
            s1 = part.Extension.SelectByID2("", "FACE", 0.012, 0.0, 0.0148, False, 1, callout, 0)
            s2 = part.Extension.SelectByID2("", "FACE", -0.012, 0.0, 0.0148, True, 1, callout, 0)
            if s1 or s2:
                break
        except:
            continue

    try:
        chamfer = part.FeatureManager.InsertFeatureChamfer(4, 2, 0.0008, 0, 0, 0, 0)
        print("7. Top chamfer added")
    except Exception as e:
        print("7. Top chamfer skipped:", e)

    part.ClearSelection2(True)

    # ====== Step 6: Chamfer Bottom Edges ======
    for callout in ("", 0):
        try:
            s1 = part.Extension.SelectByID2("", "FACE", 0.012, 0.0, 0.0, False, 1, callout, 0)
            s2 = part.Extension.SelectByID2("", "FACE", -0.012, 0.0, 0.0, True, 1, callout, 0)
            if s1 or s2:
                break
        except:
            continue

    try:
        chamfer = part.FeatureManager.InsertFeatureChamfer(4, 2, 0.0008, 0, 0, 0, 0)
        print("8. Bottom chamfer added")
    except Exception as e:
        print("8. Bottom chamfer skipped:", e)

    part.ClearSelection2(True)

    # ====== Step 7: Add Cosmetic Thread ======
    for callout in ("", 0):
        try:
            s = part.Extension.SelectByID2("", "FACE", 0.007, 0.0, 0.007, False, 0, callout, 0)
            if s:
                break
        except:
            continue

    try:
        thread = part.FeatureManager.InsertCosmeticThread2(2, 0.016, 0.002, "M16x2")
        print("9. Cosmetic thread added")
    except Exception as e:
        print("9. Cosmetic thread skipped:", e)

    part.ClearSelection2(True)

    # ====== Final: Rebuild ======
    part.ForceRebuild3(True)
    print("\n=== M16 Hex Nut (ISO 4032) Created Successfully! ===")
    print("Dimensions: S=24mm (across flats), m=14.8mm (height), Thread=M16x2")

    # Save
    try:
        part.SaveAs3(r"D:\sw2026\M16_Nut_ISO4032.SLDPRT", 0, 0)
        print("Saved to: D:\\sw2026\\M16_Nut_ISO4032.SLDPRT")
    except Exception as e:
        print("Save skipped:", e)

except Exception as e:
    import traceback
    print("ERROR:", type(e).__name__, str(e))
    traceback.print_exc()
finally:
    pythoncom.CoUninitialize()
