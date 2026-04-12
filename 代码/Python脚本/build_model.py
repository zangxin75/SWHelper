# -*- coding: utf-8 -*-
"""Build complete 3D model from 2D drawing - SW2026 compatible via pywin32"""
import pythoncom
pythoncom.CoInitialize()
import win32com.client.dynamic as dyn
import math
import sys

swApp = dyn.Dispatch('SldWorks.Application')
swModel = swApp.ActiveDoc
skMgr = swModel.SketchManager
selMgr = swModel.SelectionManager
print("Active doc ready")

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
    """Select the face with upward normal (Y > 0) from given feature"""
    faces = feat.GetFaces
    for face in faces:
        normal = face.Normal
        if normal[1] > 0.9:
            face.Select4(False, selMgr.CreateSelectData)
            return True
    return False

def select_bottom_face_of_feature(feat):
    """Select the face with downward normal (Y < 0) from given feature"""
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
    """Select sketch and extrude/cut"""
    sketch.Select2(False, 0)
    if cut:
        return cut_extrude(depth, through_all)
    else:
        return boss_extrude(depth)

# ============================================================
# STEP 1: Base flange 190x162mm, 20mm thick
# ============================================================
print("\n--- Step 1: Base Flange 190x162x20mm ---")
planes = get_planes()
enter_sketch_on_plane(planes[1])  # Top Plane
skMgr.CreateCornerRectangle(-0.095, -0.081, 0, 0.095, 0.081, 0)
print("Rectangle drawn")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 20)
print("Base extrusion:", "SUCCESS" if res else "FAILED")
if not res:
    sys.exit(1)

# Get the base extrusion feature for face selection
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

# Get cylinder feature
cyl_extrusions = find_features_by_type('Extrusion')
cyl_feat = cyl_extrusions[-1]

# ============================================================
# STEP 3: Bore ID=150mm, depth 106mm from top
# ============================================================
print("\n--- Step 3: Bore ID150 x 106mm ---")
select_top_face_of_feature(cyl_feat)
swModel.InsertSketch2(True)
skMgr.CreateCircleByRadius(0, 0, 0, 0.075)
print("Bore circle drawn ID150mm")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 106, cut=True)
print("Bore cut:", "SUCCESS" if res else "FAILED")

# ============================================================
# STEP 4: 6 bolt holes on cylinder top, PCD~170mm, 9mm dia
# ============================================================
print("\n--- Step 4: 6 Bolt Holes ---")
select_top_face_of_feature(cyl_feat)
swModel.InsertSketch2(True)

pcd_r = 0.085   # 85mm PCD radius
hole_r = 0.0045  # 4.5mm = 9mm dia
for i in range(6):
    angle = math.radians(i * 60)
    cx = pcd_r * math.cos(angle)
    cy = pcd_r * math.sin(angle)
    skMgr.CreateCircleByRadius(cx, cy, 0, hole_r)
print("6 bolt holes drawn")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 30, cut=True, through_all=True)
print("Bolt holes cut:", "SUCCESS" if res else "FAILED")

# ============================================================
# STEP 5: 2 mounting holes on base bottom, 9mm dia, 94mm apart
# ============================================================
print("\n--- Step 5: 2 Mounting Holes ---")
select_bottom_face_of_feature(base_feat)
swModel.InsertSketch2(True)

offset = 0.047  # 47mm from center
skMgr.CreateCircleByRadius(-offset, 0, 0, 0.0045)
skMgr.CreateCircleByRadius( offset, 0, 0, 0.0045)
print("2 mounting holes drawn")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 30, cut=True, through_all=True)
print("Mounting holes cut:", "SUCCESS" if res else "FAILED")

# ============================================================
# STEP 6: 2 M6 tapped holes on top, 88mm apart, 12.5mm deep
# ============================================================
print("\n--- Step 6: 2 M6 Tapped Holes ---")
select_top_face_of_feature(cyl_feat)
swModel.InsertSketch2(True)

m6_off = 0.044  # 44mm from center (88/2)
skMgr.CreateCircleByRadius(-m6_off, 0, 0, 0.003)
skMgr.CreateCircleByRadius( m6_off, 0, 0, 0.003)
print("2 M6 holes drawn")
exit_sketch()

sketch = find_last_sketch()
res = extrude_sketch(sketch, 12.5, cut=True)
print("M6 holes cut:", "SUCCESS" if res else "FAILED")

print("\n=== Model building complete! ===")
print("Features created: Base flange, Cylinder body, Bore, 6 Bolt holes, 2 Mounting holes, 2 M6 tapped holes")
