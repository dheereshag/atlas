# /// script
# dependencies = []
# ///
"""
Ultra-Modern & Futuristic 3D-Printable Enclosure Generator for Blender (bpy)
Features advanced 3D-printable industrial design geometry:
1. Enclosure Base with 2.5mm double-chamfered fillets, port-aware side grooves, chamfered port bezels (DB9 & Micro-USB), rear aero-vents & flush rubber feet sockets
2. Ultra-Stylish Top Lid with dual-plane recessed border, debossed sci-fi accent lines, counter-bored M3 screw sockets, chamfered status badge channel, 1x 0.56-inch 7-segment LED cutout and 1x 5.2mm RGB LED cutout, and honeycomb vent grid
3. Clearance Reference PCB Mockups (LM2596, MAX3232, ESP32)
4. Single uniform 3D-printable filament material (Mat_3D_Print_Filament)
"""

import socket
import json
import sys

BLENDER_ENCLOSURE_SCRIPT = """
import bpy
import os
import math

# ---------------------------------------------------------
# 0. Clean Existing Scene
# ---------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for collection in [bpy.data.meshes, bpy.data.materials]:
    for block in list(collection):
        if block.users == 0:
            collection.remove(block)

# ---------------------------------------------------------
# Single Uniform 3D Printing Filament Material
# ---------------------------------------------------------
def get_3d_print_material():
    mat_name = "Mat_3D_Print_Filament"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.18, 0.20, 0.24, 1.0)
            if 'Roughness' in bsdf.inputs:
                bsdf.inputs['Roughness'].default_value = 0.35
    return mat

mat_filament = get_3d_print_material()

# ---------------------------------------------------------
# Enclosure Specs (in mm)
# ---------------------------------------------------------
outer_l = 120.0  # X-axis length
outer_w = 90.0   # Y-axis width
outer_h = 28.0   # Z-axis height
wall_t = 2.0     # Wall thickness
floor_t = 2.0    # Floor thickness
standoff_h = 4.0 # Height of PCB standoffs from floor

inner_l = outer_l - 2 * wall_t
inner_w = outer_w - 2 * wall_t
inner_h = outer_h - floor_t

# ---------------------------------------------------------
# 1. Futuristic 3D Printable Enclosure Base Body
# ---------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, outer_h / 2.0))
base_obj = bpy.context.active_object
base_obj.name = "Enclosure_Base"
base_obj.scale = (outer_l, outer_w, outer_h)
bpy.ops.object.transform_apply(scale=True)
base_obj.data.materials.append(mat_filament)

# Inner Cavity Cutter
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, floor_t + inner_h / 2.0 + 0.1))
cavity_obj = bpy.context.active_object
cavity_obj.name = "Inner_Cavity_Cutter"
cavity_obj.scale = (inner_l, inner_w, inner_h + 0.2)
bpy.ops.object.transform_apply(scale=True)

# Subtract Cavity from Base
bool_mod = base_obj.modifiers.new(name="Cavity_Subtract", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = cavity_obj
bpy.ops.object.select_all(action='DESELECT')
base_obj.select_set(True)
bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_apply(modifier="Cavity_Subtract")
bpy.data.objects.remove(cavity_obj, do_unlink=True)

# Port-Aware Side Accent Grooves (Left Wall & Right Wall Ends Only)
for k in [-2, -1, 0, 1, 2]:
    gy = k * 7.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-outer_l / 2.0, gy, outer_h / 2.0 + 1.0))
    grip = bpy.context.active_object
    grip.scale = (1.4, 2.8, outer_h - 8.0)
    bpy.ops.object.transform_apply(scale=True)
    
    mod_g = base_obj.modifiers.new(name="Grip_Subtract_L", type='BOOLEAN')
    mod_g.operation = 'DIFFERENCE'
    mod_g.object = grip
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier="Grip_Subtract_L")
    bpy.data.objects.remove(grip, do_unlink=True)

for gy in [-20.0, -14.0, 14.0, 20.0]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(outer_l / 2.0, gy, outer_h / 2.0 + 1.0))
    grip = bpy.context.active_object
    grip.scale = (1.4, 2.8, outer_h - 8.0)
    bpy.ops.object.transform_apply(scale=True)
    
    mod_g = base_obj.modifiers.new(name="Grip_Subtract_R", type='BOOLEAN')
    mod_g.operation = 'DIFFERENCE'
    mod_g.object = grip
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier="Grip_Subtract_R")
    bpy.data.objects.remove(grip, do_unlink=True)

# Rear Aero-Vent Slits on Back Wall (Y = +35mm)
for k in [-1, 0, 1]:
    rx = k * 14.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, outer_w / 2.0, outer_h / 2.0 + 2.0))
    r_vent = bpy.context.active_object
    r_vent.scale = (8.0, wall_t * 3.0, 3.5)
    bpy.ops.object.transform_apply(scale=True)
    
    mod_rv = base_obj.modifiers.new(name="Rear_Vent", type='BOOLEAN')
    mod_rv.operation = 'DIFFERENCE'
    mod_rv.object = r_vent
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier="Rear_Vent")
    bpy.data.objects.remove(r_vent, do_unlink=True)

# 4x Base Tactical Corner Facet Cuts
for cx_sign, cy_sign in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
    px = cx_sign * (outer_l / 2.0)
    py = cy_sign * (outer_w / 2.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, outer_h / 2.0))
    cf = bpy.context.active_object
    cf.scale = (8.0, 8.0, outer_h + 2.0)
    cf.rotation_euler = (0, 0, math.radians(45))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    
    mod_cf = base_obj.modifiers.new(name="Corner_Facet", type='BOOLEAN')
    mod_cf.operation = 'DIFFERENCE'
    mod_cf.object = cf
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier="Corner_Facet")
    bpy.data.objects.remove(cf, do_unlink=True)

# 4x Bottom Rubber Base Pad Recessed Sockets
corner_margin_x = outer_l / 2.0 - 4.5
corner_margin_y = outer_w / 2.0 - 4.5
corner_coords = [
    (-corner_margin_x, -corner_margin_y),
    ( corner_margin_x, -corner_margin_y),
    (-corner_margin_x,  corner_margin_y),
    ( corner_margin_x,  corner_margin_y)
]

for i, (cx, cy) in enumerate(corner_coords):
    bpy.ops.mesh.primitive_cylinder_add(radius=4.6, depth=1.0, location=(cx, cy, 0.5))
    soc = bpy.context.active_object
    mod_soc = base_obj.modifiers.new(name=f"Recess_{i+1}", type='BOOLEAN')
    mod_soc.operation = 'DIFFERENCE'
    mod_soc.object = soc
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier=f"Recess_{i+1}")
    bpy.data.objects.remove(soc, do_unlink=True)

# ---------------------------------------------------------
# 2. Internal Standoffs & Corner Posts
# ---------------------------------------------------------
for i, (cx, cy) in enumerate(corner_coords):
    bpy.ops.mesh.primitive_cylinder_add(radius=4.0, depth=inner_h, location=(cx, cy, floor_t + inner_h / 2.0))
    post = bpy.context.active_object
    post.name = f"Corner_Post_{i+1}"
    
    # M3 Hole
    bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=inner_h + 1.0, location=(cx, cy, floor_t + inner_h / 2.0))
    hole = bpy.context.active_object
    
    mod = post.modifiers.new(name="M3_Hole", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = hole
    bpy.ops.object.select_all(action='DESELECT')
    post.select_set(True)
    bpy.context.view_layer.objects.active = post
    bpy.ops.object.modifier_apply(modifier="M3_Hole")
    bpy.data.objects.remove(hole, do_unlink=True)
    
    # Join post to Base
    mod_join = base_obj.modifiers.new(name=f"Join_Post_{i+1}", type='BOOLEAN')
    mod_join.operation = 'UNION'
    mod_join.object = post
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier=f"Join_Post_{i+1}")
    bpy.data.objects.remove(post, do_unlink=True)

# Function to add standoff posts with M3 pilot holes to base
def add_standoff_posts(base_object, coords, prefix, radius=3.0, height=standoff_h, pilot_r=1.4):
    for i, (px, py) in enumerate(coords):
        z_pos = floor_t + height / 2.0
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=(px, py, z_pos))
        st_post = bpy.context.active_object
        st_post.name = f"{prefix}_Standoff_{i+1}"
        
        # Inner M3 pilot hole
        bpy.ops.mesh.primitive_cylinder_add(radius=pilot_r, depth=height + 2.0, location=(px, py, z_pos))
        st_hole = bpy.context.active_object
        
        mod_h = st_post.modifiers.new(name="Pilot_Hole", type='BOOLEAN')
        mod_h.operation = 'DIFFERENCE'
        mod_h.object = st_hole
        bpy.ops.object.select_all(action='DESELECT')
        st_post.select_set(True)
        bpy.context.view_layer.objects.active = st_post
        bpy.ops.object.modifier_apply(modifier="Pilot_Hole")
        bpy.data.objects.remove(st_hole, do_unlink=True)
        
        # Join standoff to Base
        mod_j = base_object.modifiers.new(name=f"Join_{prefix}_{i+1}", type='BOOLEAN')
        mod_j.operation = 'UNION'
        mod_j.object = st_post
        bpy.context.view_layer.objects.active = base_object
        bpy.ops.object.modifier_apply(modifier=f"Join_{prefix}_{i+1}")
        bpy.data.objects.remove(st_post, do_unlink=True)

# Layout Coordinates for All 3 Modules
lm_cx, lm_cy = -25.0, 22.0
lm_coords = [
    (lm_cx - 18.0, lm_cy + 10.0),
    (lm_cx + 18.0, lm_cy - 10.0)
]
add_standoff_posts(base_obj, lm_coords, "LM2596")

max_cx, max_cy = -26.0, -22.0
max_coords = [
    (max_cx - 13.5, max_cy - 13.0),
    (max_cx + 13.5, max_cy - 13.0),
    (max_cx - 13.5, max_cy + 13.0),
    (max_cx + 13.5, max_cy + 13.0)
]
add_standoff_posts(base_obj, max_coords, "MAX3232")

esp_cx, esp_cy = 28.0, 0.0
esp_coords = [
    (esp_cx - 11.75, esp_cy - 23.25),
    (esp_cx + 11.75, esp_cy - 23.25),
    (esp_cx - 11.75, esp_cy + 23.25),
    (esp_cx + 11.75, esp_cy + 23.25)
]
add_standoff_posts(base_obj, esp_coords, "ESP32")

# Apply Smooth 2.5mm Chamfer/Bevel to Base Outer Edges
mod_b = base_obj.modifiers.new(name="Bevel_Base", type='BEVEL')
mod_b.width = 2.5
mod_b.segments = 4
mod_b.limit_method = 'ANGLE'
mod_b.angle_limit = math.radians(40)
bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_apply(modifier="Bevel_Base")

# ---------------------------------------------------------
# 3. Port Cutouts with Chamfered Port Bezels (DB9 Front & Micro-USB Side)
# ---------------------------------------------------------
# DB9 Cutout on Front Wall with 45-degree Chamfer Bezel
db9_w, db9_h = 31.5, 14.0
db9_z_center = floor_t + standoff_h + 2.0 + db9_h / 2.0  # Z = 15.0mm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(max_cx, -outer_w / 2.0, db9_z_center))
db9_cutter = bpy.context.active_object
db9_cutter.scale = (db9_w, wall_t * 3.0, db9_h)
bpy.ops.object.transform_apply(scale=True)

mod_db9 = base_obj.modifiers.new(name="DB9_Cutout", type='BOOLEAN')
mod_db9.operation = 'DIFFERENCE'
mod_db9.object = db9_cutter
bpy.ops.object.select_all(action='DESELECT')
base_obj.select_set(True)
bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_apply(modifier="DB9_Cutout")
bpy.data.objects.remove(db9_cutter, do_unlink=True)

# Outer DB9 Chamfer Bezel Cutter
bpy.ops.mesh.primitive_cone_add(radius1=18.0, radius2=16.0, depth=1.2, location=(max_cx, -outer_w / 2.0 - 0.2, db9_z_center), rotation=(math.radians(90), 0, 0))
db9_bez = bpy.context.active_object
db9_bez.scale = (1.0, 1.0, 0.8)
bpy.ops.object.transform_apply(scale=True)

mod_db9_b = base_obj.modifiers.new(name="DB9_Bezel_Cut", type='BOOLEAN')
mod_db9_b.operation = 'DIFFERENCE'
mod_db9_b.object = db9_bez
bpy.ops.object.select_all(action='DESELECT')
base_obj.select_set(True)
bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_apply(modifier="DB9_Bezel_Cut")
bpy.data.objects.remove(db9_bez, do_unlink=True)

# Micro-USB Cutout on Right Side Wall with Chamfer Bezel
usb_w, usb_h = 10.5, 7.5
usb_y_pos = esp_cy
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(outer_l / 2.0, usb_y_pos, floor_t + 4.0 + usb_h / 2.0))
usb_cutter = bpy.context.active_object
usb_cutter.scale = (wall_t * 3.0, usb_w, usb_h)
bpy.ops.object.transform_apply(scale=True)

mod_usb = base_obj.modifiers.new(name="USB_Cutout", type='BOOLEAN')
mod_usb.operation = 'DIFFERENCE'
mod_usb.object = usb_cutter
bpy.ops.object.select_all(action='DESELECT')
base_obj.select_set(True)
bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_apply(modifier="USB_Cutout")
bpy.data.objects.remove(usb_cutter, do_unlink=True)

# Outer Micro-USB Chamfer Bezel Cutter
bpy.ops.mesh.primitive_cone_add(radius1=6.5, radius2=5.0, depth=1.0, location=(outer_l / 2.0 + 0.2, usb_y_pos, floor_t + 4.0 + usb_h / 2.0), rotation=(0, math.radians(90), 0))
usb_bez = bpy.context.active_object
usb_bez.scale = (1.0, 0.8, 1.0)
bpy.ops.object.transform_apply(scale=True)

mod_usb_b = base_obj.modifiers.new(name="USB_Bezel_Cut", type='BOOLEAN')
mod_usb_b.operation = 'DIFFERENCE'
mod_usb_b.object = usb_bez
bpy.ops.object.select_all(action='DESELECT')
base_obj.select_set(True)
bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.modifier_apply(modifier="USB_Bezel_Cut")
bpy.data.objects.remove(usb_bez, do_unlink=True)

# ---------------------------------------------------------
# 4. Ultra-Stylish Top Lid with Sci-Fi Debossed Accents & Sockets
# ---------------------------------------------------------
lid_h = 2.8
lid_z = outer_h + lid_h / 2.0 + 5.0  # Displayed 5mm above base
lid_z_top = lid_z + lid_h / 2.0

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, lid_z))
lid_obj = bpy.context.active_object
lid_obj.name = "Enclosure_Top_Lid"
lid_obj.scale = (outer_l, outer_w, lid_h)
bpy.ops.object.transform_apply(scale=True)
lid_obj.data.materials.append(mat_filament)

# Dual-Plane Recessed Center Border
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, lid_z_top - 0.4))
top_recess = bpy.context.active_object
top_recess.scale = (outer_l - 8.0, outer_w - 8.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

mod_tr = lid_obj.modifiers.new(name="Top_Border_Recess", type='BOOLEAN')
mod_tr.operation = 'DIFFERENCE'
mod_tr.object = top_recess
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="Top_Border_Recess")
bpy.data.objects.remove(top_recess, do_unlink=True)

# Debossed Geometric Sci-Fi Accent Lines
for line_y in [-18.0, 18.0]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, line_y, lid_z_top - 0.2))
    line_cut = bpy.context.active_object
    line_cut.scale = (outer_l - 12.0, 0.8, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    
    mod_lc = lid_obj.modifiers.new(name="Debossed_Line", type='BOOLEAN')
    mod_lc.operation = 'DIFFERENCE'
    mod_lc.object = line_cut
    bpy.ops.object.select_all(action='DESELECT')
    lid_obj.select_set(True)
    bpy.context.view_layer.objects.active = lid_obj
    bpy.ops.object.modifier_apply(modifier="Debossed_Line")
    bpy.data.objects.remove(line_cut, do_unlink=True)

# Apply Double-Stepped Bevel to Top Lid Edges
mod_lb = lid_obj.modifiers.new(name="Bevel_Lid", type='BEVEL')
mod_lb.width = 1.8
mod_lb.segments = 4
mod_lb.limit_method = 'ANGLE'
mod_lb.angle_limit = math.radians(40)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="Bevel_Lid")

# 4x Lid Corner Screw Holes with Flush Counter-Bore Sockets
for cx, cy in corner_coords:
    # Through-hole
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=lid_h + 1.0, location=(cx, cy, lid_z))
    sc_hole = bpy.context.active_object
    
    mod_sc = lid_obj.modifiers.new(name="Screw_Hole", type='BOOLEAN')
    mod_sc.operation = 'DIFFERENCE'
    mod_sc.object = sc_hole
    bpy.ops.object.select_all(action='DESELECT')
    lid_obj.select_set(True)
    bpy.context.view_layer.objects.active = lid_obj
    bpy.ops.object.modifier_apply(modifier="Screw_Hole")
    bpy.data.objects.remove(sc_hole, do_unlink=True)
    
    # Counter-bore chamfer socket for flush M3 head
    bpy.ops.mesh.primitive_cylinder_add(radius=3.0, depth=1.2, location=(cx, cy, lid_z_top - 0.6))
    cb_socket = bpy.context.active_object
    mod_cb = lid_obj.modifiers.new(name="CB_Socket", type='BOOLEAN')
    mod_cb.operation = 'DIFFERENCE'
    mod_cb.object = cb_socket
    bpy.ops.object.select_all(action='DESELECT')
    lid_obj.select_set(True)
    bpy.context.view_layer.objects.active = lid_obj
    bpy.ops.object.modifier_apply(modifier="CB_Socket")
    bpy.data.objects.remove(cb_socket, do_unlink=True)

# Hexagonal Thermal Vent Grid Array
hex_r = 2.2
for row in range(-2, 3):
    for col in range(-3, 4):
        hx = col * 5.2 + (2.6 if row % 2 != 0 else 0)
        hy = row * 4.5 + 8.0
        
        # Skip GLUVOK badge region & LED panel region
        if hy < -14.0 or hy > 18.0:
            continue
            
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=hex_r, depth=lid_h + 2.0, location=(hx, hy, lid_z))
        hex_vent = bpy.context.active_object
        
        mod_h = lid_obj.modifiers.new(name="Hex_Vent", type='BOOLEAN')
        mod_h.operation = 'DIFFERENCE'
        mod_h.object = hex_vent
        bpy.ops.object.select_all(action='DESELECT')
        lid_obj.select_set(True)
        bpy.context.view_layer.objects.active = lid_obj
        bpy.ops.object.modifier_apply(modifier="Hex_Vent")
        bpy.data.objects.remove(hex_vent, do_unlink=True)

# ---------------------------------------------------------
# Recessed Status Badge Channel & Dual Cutouts
# ---------------------------------------------------------
seg_panel_y = -22.0
seg_x = -10.0
rgb_x = 12.0
seg_w, seg_h = 13.0, 19.5

# Combined Recessed Status Badge Channel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.0, seg_panel_y, lid_z_top - 0.4))
inlay_cutter = bpy.context.active_object
inlay_cutter.scale = (42.0, 24.5, 1.2)
bpy.ops.object.transform_apply(scale=True)

mod_inl = lid_obj.modifiers.new(name="LED_Inlay_Recess", type='BOOLEAN')
mod_inl.operation = 'DIFFERENCE'
mod_inl.object = inlay_cutter
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="LED_Inlay_Recess")
bpy.data.objects.remove(inlay_cutter, do_unlink=True)

# ---------------------------------------------------------
# GLUVOK Corporate Branding (Direct 3D Engraved Debossing into Lid)
# ---------------------------------------------------------
# Primary Top Lid Engraving "G L U V O K"
bpy.ops.object.text_add(location=(0.0, 26.0, lid_z_top))
txt_brand = bpy.context.active_object
txt_brand.name = "Text_GLUVOK_Engrave"
txt_brand.data.body = "G L U V O K"
txt_brand.data.size = 5.2
txt_brand.data.extrude = 1.2
txt_brand.data.align_x = 'CENTER'
txt_brand.data.align_y = 'CENTER'

bpy.ops.object.select_all(action='DESELECT')
txt_brand.select_set(True)
bpy.context.view_layer.objects.active = txt_brand
bpy.ops.object.convert(target='MESH')

txt_brand.location.z = lid_z_top - 0.4

mod_eng = lid_obj.modifiers.new(name="GLUVOK_Engrave", type='BOOLEAN')
mod_eng.operation = 'DIFFERENCE'
mod_eng.object = txt_brand
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="GLUVOK_Engrave")
bpy.data.objects.remove(txt_brand, do_unlink=True)

# 1x 7-Segment Display Rectangular Cutout Hole (13.0mm x 19.5mm)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(seg_x, seg_panel_y, lid_z))
seg_cutter = bpy.context.active_object
seg_cutter.scale = (seg_w, seg_h, lid_h + 3.0)
bpy.ops.object.transform_apply(scale=True)

mod_seg = lid_obj.modifiers.new(name="7Seg_Cutout_Hole", type='BOOLEAN')
mod_seg.operation = 'DIFFERENCE'
mod_seg.object = seg_cutter
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="7Seg_Cutout_Hole")
bpy.data.objects.remove(seg_cutter, do_unlink=True)

# Outer Bezel Recess for 7-Segment Display Cutout
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(seg_x, seg_panel_y, lid_z_top - 0.3))
seg_bez = bpy.context.active_object
seg_bez.scale = (seg_w + 1.6, seg_h + 1.6, 0.8)
bpy.ops.object.transform_apply(scale=True)

mod_seg_b = lid_obj.modifiers.new(name="7Seg_Bezel_Cut", type='BOOLEAN')
mod_seg_b.operation = 'DIFFERENCE'
mod_seg_b.object = seg_bez
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="7Seg_Bezel_Cut")
bpy.data.objects.remove(seg_bez, do_unlink=True)

# 1x Physical 5.2mm RGB LED Through-Hole Cutout + Chamfer Countersink
bpy.ops.mesh.primitive_cylinder_add(radius=2.6, depth=lid_h + 3.0, location=(rgb_x, seg_panel_y, lid_z))
rgb_cutter = bpy.context.active_object

mod_rgb = lid_obj.modifiers.new(name="RGB_Cutout_Hole", type='BOOLEAN')
mod_rgb.operation = 'DIFFERENCE'
mod_rgb.object = rgb_cutter
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="RGB_Cutout_Hole")
bpy.data.objects.remove(rgb_cutter, do_unlink=True)

# Chamfered funnel countersink at top of RGB LED hole
bpy.ops.mesh.primitive_cone_add(radius1=3.2, radius2=2.6, depth=0.8, location=(rgb_x, seg_panel_y, lid_z_top - 0.4))
rgb_cs = bpy.context.active_object
mod_rgb_cs = lid_obj.modifiers.new(name="RGB_CS", type='BOOLEAN')
mod_rgb_cs.operation = 'DIFFERENCE'
mod_rgb_cs.object = rgb_cs
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="RGB_CS")
bpy.data.objects.remove(rgb_cs, do_unlink=True)

# ---------------------------------------------------------
# 5. Clearance Reference PCB Mockups
# ---------------------------------------------------------
pcb_thickness = 2.0
pcb_z_center = floor_t + standoff_h + pcb_thickness / 2.0  # Z = 7.0mm

def cut_pcb_screw_holes(pcb_obj, hole_coords, pcb_z_ctr, pcb_thick=2.0, hole_radius=1.5):
    for idx, (hx, hy) in enumerate(hole_coords):
        bpy.ops.mesh.primitive_cylinder_add(radius=hole_radius, depth=pcb_thick + 1.0, location=(hx, hy, pcb_z_ctr))
        cutter = bpy.context.active_object
        
        mod = pcb_obj.modifiers.new(name=f"Screw_Hole_{idx+1}", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        bpy.ops.object.select_all(action='DESELECT')
        pcb_obj.select_set(True)
        bpy.context.view_layer.objects.active = pcb_obj
        bpy.ops.object.modifier_apply(modifier=f"Screw_Hole_{idx+1}")
        bpy.data.objects.remove(cutter, do_unlink=True)

# MAX3232 RS232 Module Mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(max_cx, max_cy, pcb_z_center))
m_max = bpy.context.active_object
m_max.name = "Mockup_MAX3232_PCB"
m_max.scale = (32.0, 33.0, pcb_thickness)
bpy.ops.object.transform_apply(scale=True)
m_max.data.materials.append(mat_filament)
cut_pcb_screw_holes(m_max, max_coords, pcb_z_center)

db9_height = 16.0
db9_z_pos = floor_t + standoff_h + pcb_thickness + db9_height / 2.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(max_cx, -outer_w/2.0 + 5.5, db9_z_pos))
m_db9 = bpy.context.active_object
m_db9.name = "Mockup_DB9_Header"
m_db9.scale = (31.0, 11.0, db9_height)
bpy.ops.object.transform_apply(scale=True)
m_db9.data.materials.append(mat_filament)

# LM2596 Buck Converter Mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lm_cx, lm_cy, pcb_z_center))
m_lm = bpy.context.active_object
m_lm.name = "Mockup_LM2596_PCB"
m_lm.scale = (45.0, 20.0, pcb_thickness)
bpy.ops.object.transform_apply(scale=True)
m_lm.data.materials.append(mat_filament)
cut_pcb_screw_holes(m_lm, lm_coords, pcb_z_center)

# ESP32 DevKit V1 Board Mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(esp_cx, esp_cy, pcb_z_center))
m_esp = bpy.context.active_object
m_esp.name = "Mockup_ESP32_PCB"
m_esp.scale = (28.5, 51.5, pcb_thickness)
bpy.ops.object.transform_apply(scale=True)
m_esp.data.materials.append(mat_filament)
cut_pcb_screw_holes(m_esp, esp_coords, pcb_z_center)

bpy.ops.object.select_all(action='DESELECT')

result = {
    "status": "success",
    "message": "Futuristic enclosure geometry generated with chamfered DB9 & Micro-USB port bezels, rear aero-vents, sci-fi debossed lid accents, counter-bored M3 screw sockets, 1x 0.56-inch 7-segment display cutout, and 1x 5.2mm RGB LED cutout.",
    "remaining_objects_count": len(bpy.data.objects)
}
"""

def send_to_blender_mcp(host: str = "127.0.0.1", port: int = 9876):
    """Sends the enclosure generation script to the running Blender MCP server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            
            payload = json.dumps({
                "type": "execute",
                "code": BLENDER_ENCLOSURE_SCRIPT,
                "strict_json": False
            }).encode("utf-8") + b"\0"
            
            s.sendall(payload)
            
            response_data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                if b"\0" in chunk:
                    response_data += chunk.split(b"\0")[0]
                    break
                response_data += chunk
                
            response = json.loads(response_data.decode("utf-8"))
            print("Blender MCP Server Response:")
            print(json.dumps(response, indent=2))
            
    except ConnectionRefusedError:
        print(f"Error: Could not connect to Blender MCP server at {host}:{port}.")
        print("Please ensure Blender is open and the MCP server is running.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_to_blender_mcp()
