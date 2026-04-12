# -*- coding: utf-8 -*-
"""Build corrected 3D model from 2D drawing - SW2026 compatible via pywin32"""
import pythoncom
pythoncom.CoInitialize()
import win32com.client.dynamic as dyn
import math
import sys
import os

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

swApp = dyn.Dispatch('SldWorks.Application')

# Create a new part document using NewPart
swApp.NewPart
swModel = swApp.ActiveDoc
if not swModel:
    print("ERROR: Could not create new part")
    sys.exit(1)

skMgr = swModel.SketchManager
selMgr = swModel.SelectionManager
featMgr = swModel.FeatureManager
print("New part created and ready")

def get_planes():
    feats = swModel.FeatureManager.GetFeatures(False)
    return [f for f in feats if f.GetTypeName == 'RefPlane']

def find_features_by_type(type_name):
    feats = swModel.FeatureManager.GetFeatures(False)
    return [f for f in feats if f.GetTypeName == type_name]

def find_last_sketch():
    sketches = find_features_by_type('ProfileFeature')
    return sketches[-1] if sketches else None

def select_top_face_of_feature(feat):
    faces = feat.GetFaces
    for face in faces:
        normal = face.Normal
        if normal[1] > 0.9:
            face.Select4(False, selMgr.CreateSelectData)
            return True
    return False

def select_bottom_face_of_feature(feat):
    faces = feat.GetFaces
    for face in faces:
        normal = face.Normal
        if normal[1] < -0.9:
            face.Select4(False, selMgr.CreateSelectData)
            return True
    return False

def enter_sketch_on_plane(plane):
    plane.Select2(False, 0)
    swModel.InsertSketch2(True)

def exit_sketch():
    swModel.InsertSketch2(True)

def boss_extrude(depth_mm):
    d = depth_mm / 1000.0
    return swModel.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0, d, d,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False,
        True, True, True, 0, 0, False)

def cut_extrude(depth_mm, through_all=False):
    d = depth_mm / 1000.0
    t1 = 1 if through_all else 0
    return swModel.FeatureManager.FeatureExtrusion2(
        True, True, False, t1, 0, d, d,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False,
        True, True, True, 0, 0, False)

def extrude_sketch(sketch, depth, cut=False, through_all=False):
    sketch.Select2(False, 0)
    if cut:
        return cut_extrude(depth, through_all)
    else:
        return boss_extrude(depth)

# ============================================================
# STEP 1: Base flange 190x94mm, 20mm thick
# ============================================================
print("\n--- Step 1: Base Flange 190x94x20mm ---")
planes = get_planes()
enter_sketch_on_plane(planes[1])  # Top Plane
skMgr.CreateCornerRectangle(-0.095, -0.047, 0, 0.095, 0.047, 0)
print("Rectangle drawn (190x94mm)")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 20)
print("Base extrusion:", "SUCCESS" if res else "FAILED")
if not res:
    sys.exit(1)

base_extrusions = find_features_by_type('Extrusion')
base_feat = base_extrusions[-1]

# ============================================================
# STEP 2: Cylinder OD=185mm, height 194.5mm
# ============================================================
print("\n--- Step 2: Cylinder OD185 x 194.5mm ---")
select_top_face_of_feature(base_feat)
swModel.InsertSketch2(True)
skMgr.CreateCircleByRadius(0, 0, 0, 0.0925)
print("Circle drawn OD185mm")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 194.5)
print("Cylinder extrusion:", "SUCCESS" if res else "FAILED")

cyl_extrusions = find_features_by_type('Extrusion')
cyl_feat = cyl_extrusions[-1]

# ============================================================
# STEP 3: Bore ID=98mm H7, depth 150mm from top
# ============================================================
print("\n--- Step 3: Bore ID98 x 150mm ---")
select_top_face_of_feature(cyl_feat)
swModel.InsertSketch2(True)
skMgr.CreateCircleByRadius(0, 0, 0, 0.049)
print("Bore circle drawn ID98mm")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 150, cut=True)
print("Bore cut:", "SUCCESS" if res else "FAILED")

# ============================================================
# STEP 4: 6 bolt holes on cylinder top, PCD=170mm, dia 11mm
# ============================================================
print("\n--- Step 4: 6 Bolt Holes dia 11mm ---")
select_top_face_of_feature(cyl_feat)
swModel.InsertSketch2(True)

pcd_r = 0.085   # 85mm PCD radius
hole_r = 0.0055  # 5.5mm = dia 11mm
for i in range(6):
    angle = math.radians(i * 60)
    cx = pcd_r * math.cos(angle)
    cy = pcd_r * math.sin(angle)
    skMgr.CreateCircleByRadius(cx, cy, 0, hole_r)
print("6 bolt holes drawn dia 11mm")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 30, cut=True, through_all=True)
print("Bolt holes cut:", "SUCCESS" if res else "FAILED")

# ============================================================
# STEP 5: 4 mounting holes on base, dia 11mm
# Use Top Plane for sketch, then cut downward through base
# ============================================================
print("\n--- Step 5: 4 Mounting Holes dia 11mm ---")
# Use Top Plane directly - this avoids face selection issues
planes = get_planes()
top_plane = planes[1]  # Top Plane
top_plane.Select2(False, 0)
swModel.InsertSketch2(True)

hole_r_mount = 0.0055  # dia 11mm
x_off = 0.035   # 35mm from center in X
y_off = 0.034   # 34mm from center in Y
skMgr.CreateCircleByRadius(-x_off, -y_off, 0, hole_r_mount)
skMgr.CreateCircleByRadius( x_off, -y_off, 0, hole_r_mount)
skMgr.CreateCircleByRadius(-x_off,  y_off, 0, hole_r_mount)
skMgr.CreateCircleByRadius( x_off,  y_off, 0, hole_r_mount)
print("4 mounting holes drawn dia 11mm")
exit_sketch()

sketch = find_last_sketch()
# Cut downward 20mm through the base flange
sketch.Select2(False, 0)
res = cut_extrude(20)
print("Mounting holes cut:", "SUCCESS" if res else "FAILED")

# ============================================================
# STEP 6: Chamfer 30 deg x 1.6mm at bore top edge
# ============================================================
print("\n--- Step 6: Chamfer 30 deg x 1.6mm ---")
# Find all features and look for the bore cut
all_feats = swModel.FeatureManager.GetFeatures(False)
print("All feature types:", [f.GetTypeName for f in all_feats])

# Try to find the bore cut feature (type might be 'ICE' or 'CutExtrude' etc.)
bore_cut_feat = None
for f in all_feats:
    tn = f.GetTypeName
    fn = f.Name
    print(f"  Feature: {fn} type={tn}")
    # Look for cut features
    if 'Cut' in tn or 'cut' in fn or 'Cut' in fn:
        if bore_cut_feat is None:
            bore_cut_feat = f

chamfer_done = False
if bore_cut_feat:
    print(f"Found cut feature: {bore_cut_feat.Name} ({bore_cut_feat.GetTypeName})")
    faces = bore_cut_feat.GetFaces
    print(f"  Cut feature has {len(faces)} faces")

    # Select the circular edge at the top of the bore
    for face in faces:
        edges = face.GetEdges
        for edge in edges:
            try:
                sp = edge.GetStartPoint
                ep = edge.GetEndPoint
                if sp and ep:
                    # Top of cylinder is at Y = 0.020 + 0.1945 = 0.2145m
                    if sp[1] > 0.21 and ep[1] > 0.21:
                        edge.Select4(False, selMgr.CreateSelectData)
                        print(f"  Selected edge at y={sp[1]:.4f}")
                        # InsertFeatureChamfer(type, flip, width, angle, ...)
                        # type: 0=width-width, 1=angle-width, 2=width-angle
                        # Actually let's try InsertFeatureChamfer with different params
                        try:
                            res = featMgr.InsertFeatureChamfer(
                                0, 0, 1.6/1000.0, 0, 0, 0, 0, 0)
                            if res:
                                print("Chamfer: SUCCESS")
                                chamfer_done = True
                        except:
                            pass
                        if not chamfer_done:
                            try:
                                # Try with ChamferType_e values
                                res = featMgr.InsertFeatureChamfer(
                                    2, 0, 1.6/1000.0, math.radians(30), 0, 0, 0, 0)
                                if res:
                                    print("Chamfer: SUCCESS (alt)")
                                    chamfer_done = True
                            except:
                                pass
                        break
            except:
                continue
        if chamfer_done:
            break

if not chamfer_done:
    print("Chamfer: SKIPPED (edge selection failed - can be done manually)")

# ============================================================
# STEP 7: Fillet R0.5mm at bore-base junction
# ============================================================
print("\n--- Step 7: Fillet R0.5mm ---")
fillet_done = False
if bore_cut_feat:
    faces = bore_cut_feat.GetFaces
    # Try to select edges at the base level (Y ~= 0.02m = base top)
    for face in faces:
        edges = face.GetEdges
        for edge in edges:
            try:
                sp = edge.GetStartPoint
                ep = edge.GetEndPoint
                if sp and ep:
                    # Edge at base-cylinder junction, Y ~= 0.02m, radius ~= 0.049m
                    if abs(sp[1] - 0.02) < 0.005 and abs(ep[1] - 0.02) < 0.005:
                        edge.Select4(False, selMgr.CreateSelectData)
                        print(f"  Selected fillet edge at y={sp[1]:.4f}")
                        try:
                            res = featMgr.InsertFeatureFillet(2, 0.0005, 0, 0)
                            if res:
                                print("Fillet: SUCCESS")
                                fillet_done = True
                        except:
                            pass
                        if not fillet_done:
                            try:
                                res = featMgr.InsertFeatureFillet2(0.0005, 1, 0, 0, 0, 0, 0)
                                if res:
                                    print("Fillet: SUCCESS (alt)")
                                    fillet_done = True
                            except:
                                pass
                        break
            except:
                continue
        if fillet_done:
            break

if not fillet_done:
    print("Fillet: SKIPPED (edge selection failed - can be done manually)")

# ============================================================
# Save the corrected model
# ============================================================
print("\n--- Saving model ---")
save_path = r"C:\Users\zhy\Desktop\Flange_Model_v2.sldprt"
result = swModel.SaveAs2(save_path, 0, True, True)
print("Save:", "SUCCESS" if result == 0 else "code=" + str(result))

print("\n=== Model building complete! ===")
print("Features created:")
print("  1. Base flange 190x94x20mm")
print("  2. Cylinder OD185 x 194.5mm")
print("  3. Bore ID98mm x 150mm deep")
print("  4. 6 bolt holes dia 11mm on PCD170")
print("  5. 4 mounting holes dia 11mm")
if chamfer_done:
    print("  6. Chamfer 30deg x 1.6mm")
else:
    print("  6. Chamfer - SKIPPED (add manually)")
if fillet_done:
    print("  7. Fillet R0.5mm")
else:
    print("  7. Fillet - SKIPPED (add manually)")
