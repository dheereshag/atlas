# /// script
# dependencies = []
# ///
"""
Custom 3D Printed Desktop Enclosure Generator for Blender (bpy)
Generates color-coded objects with non-overlapping module layout, screw mounting holes & 3D M3 screws:
1. Enclosure Base with internal standoff posts for all modules (Dark Charcoal)
2. Enclosure Top Lid with ventilation & corner screw holes (Slate Grey)
3. LM2596 Buck Converter PCB with 2x M3 mounting holes (Royal Blue)
4. MAX3232 RS232 PCB with 4x M3 mounting holes (Teal)
5. MAX3232 DB9 Connector Header (Metallic Silver)
6. ESP32 DevKit V1 PCB with 4x M3 mounting holes (Matte Black)
7. 14x 3D M3 Pan-Head Mounting Screws (Polished Steel)
"""

import socket
import json
import sys

BLENDER_ENCLOSURE_SCRIPT = """
import bpy
import os

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
# Distinct Color Materials
# ---------------------------------------------------------
def create_color_material(name, color, metallic=0.0, roughness=0.3):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            if 'Metallic' in bsdf.inputs:
                bsdf.inputs['Metallic'].default_value = metallic
            if 'Roughness' in bsdf.inputs:
                bsdf.inputs['Roughness'].default_value = roughness
    return mat

mat_enclosure_base = create_color_material("Mat_Enclosure_Base", (0.08, 0.09, 0.12, 1.0), metallic=0.0, roughness=0.35)
mat_enclosure_lid  = create_color_material("Mat_Enclosure_Lid", (0.18, 0.22, 0.28, 1.0), metallic=0.0, roughness=0.30)
mat_lm2596         = create_color_material("Mat_LM2596_Blue", (0.02, 0.15, 0.70, 1.0), metallic=0.1, roughness=0.20)
mat_max3232        = create_color_material("Mat_MAX3232_Teal", (0.0, 0.40, 0.48, 1.0), metallic=0.1, roughness=0.20)
mat_db9_header     = create_color_material("Mat_DB9_SilverMetal", (0.85, 0.85, 0.88, 1.0), metallic=0.9, roughness=0.15)
mat_esp32          = create_color_material("Mat_ESP32_MatteBlack", (0.015, 0.015, 0.015, 1.0), metallic=0.05, roughness=0.25)
mat_m3_screw       = create_color_material("Mat_M3_SteelScrew", (0.80, 0.82, 0.85, 1.0), metallic=0.95, roughness=0.10)

# Helper function to create 3D M3 Screw
def create_m3_screw(name, x, y, head_z, shaft_len=6.0):
    head_h = 1.8
    head_r = 2.75
    shaft_r = 1.4
    
    # Screw Head
    bpy.ops.mesh.primitive_cylinder_add(radius=head_r, depth=head_h, location=(x, y, head_z + head_h/2.0))
    s_head = bpy.context.active_object
    
    # Screw Shaft
    bpy.ops.mesh.primitive_cylinder_add(radius=shaft_r, depth=shaft_len, location=(x, y, head_z - shaft_len/2.0))
    s_shaft = bpy.context.active_object
    
    # Join Head and Shaft
    mod = s_head.modifiers.new(name="Join_Shaft", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = s_shaft
    bpy.context.view_layer.objects.active = s_head
    bpy.ops.object.modifier_apply(modifier="Join_Shaft")
    bpy.data.objects.remove(s_shaft, do_unlink=True)
    
    s_head.name = name
    s_head.data.materials.append(mat_m3_screw)
    return s_head

# ---------------------------------------------------------
# Enclosure Specs (in mm)
# ---------------------------------------------------------
outer_l = 90.0   # X-axis length
outer_w = 70.0   # Y-axis width
outer_h = 24.0   # Z-axis height
wall_t = 2.0     # Wall thickness
floor_t = 2.0    # Floor thickness
standoff_h = 4.0 # Height of PCB standoffs from floor

inner_l = outer_l - 2 * wall_t
inner_w = outer_w - 2 * wall_t
inner_h = outer_h - floor_t

# ---------------------------------------------------------
# 1. Main Enclosure Base Body
# ---------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, outer_h / 2.0))
base_obj = bpy.context.active_object
base_obj.name = "Enclosure_Base"
base_obj.scale = (outer_l, outer_w, outer_h)
bpy.ops.object.transform_apply(scale=True)
base_obj.data.materials.append(mat_enclosure_base)

# Create Inner Cavity Cutter
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

# ---------------------------------------------------------
# 2. Internal Standoffs & Corner Posts
# ---------------------------------------------------------
# 4x Enclosure Lid Corner Posts
corner_margin_x = outer_l / 2.0 - 4.5
corner_margin_y = outer_w / 2.0 - 4.5
corner_coords = [
    (-corner_margin_x, -corner_margin_y),
    ( corner_margin_x, -corner_margin_y),
    (-corner_margin_x,  corner_margin_y),
    ( corner_margin_x,  corner_margin_y)
]

for i, (cx, cy) in enumerate(corner_coords):
    bpy.ops.mesh.primitive_cylinder_add(radius=4.0, depth=inner_h, location=(cx, cy, floor_t + inner_h / 2.0))
    post = bpy.context.active_object
    post.name = f"Corner_Post_{i+1}"
    post.data.materials.append(mat_enclosure_base)
    
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

# Function to add standoff posts to base
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

# ---------------------------------------------------------
# Non-Overlapping Layout Coordinates for All 3 Modules
# ---------------------------------------------------------
# LM2596 Buck Converter (Back Left)
lm_cx, lm_cy = -18.0, 18.0
lm_coords = [
    (lm_cx - 18.0, lm_cy - 10.0),
    (lm_cx + 18.0, lm_cy + 10.0)
]
add_standoff_posts(base_obj, lm_coords, "LM2596")

# MAX3232 RS232 Module (Front Left)
max_cx, max_cy = -20.0, -16.0
max_coords = [
    (max_cx - 13.5, max_cy - 13.0),
    (max_cx + 13.5, max_cy - 13.0),
    (max_cx - 13.5, max_cy + 13.0),
    (max_cx + 13.5, max_cy + 13.0)
]
add_standoff_posts(base_obj, max_coords, "MAX3232")

# ESP32 DevKit V1 Board (Right Side)
esp_cx, esp_cy = 24.0, 0.0
esp_coords = [
    (esp_cx - 11.75, esp_cy - 23.25),
    (esp_cx + 11.75, esp_cy - 23.25),
    (esp_cx - 11.75, esp_cy + 23.25),
    (esp_cx + 11.75, esp_cy + 23.25)
]
add_standoff_posts(base_obj, esp_coords, "ESP32")

# ---------------------------------------------------------
# 3. Port Cutouts (DB9 Front & Micro-USB Side)
# ---------------------------------------------------------
# DB9 Cutout on Front Wall (aligned with MAX3232 at X = -20.0)
db9_w, db9_h = 31.5, 15.5
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(max_cx, -outer_w / 2.0, floor_t + 4.0 + db9_h / 2.0))
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

# Micro-USB Cutout on Right Side Wall (aligned with ESP32 at Y = 0.0)
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

# ---------------------------------------------------------
# 4. Ventilated Top Lid & Corner Lid Screws
# ---------------------------------------------------------
lid_h = 2.5
lid_z = outer_h + lid_h / 2.0 + 5.0  # Displayed 5mm above base

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, lid_z))
lid_obj = bpy.context.active_object
lid_obj.name = "Enclosure_Top_Lid"
lid_obj.scale = (outer_l, outer_w, lid_h)
bpy.ops.object.transform_apply(scale=True)
lid_obj.data.materials.append(mat_enclosure_lid)

# 4x Lid Corner Screw Holes & Screws
for cx, cy in corner_coords:
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
    
    # Create 3D Screw for Lid Corner
    create_m3_screw(f"Screw_Lid_Corner_({cx:.0f},{cy:.0f})", cx, cy, lid_z + lid_h/2.0, shaft_len=8.0)

# Linear Thermal Ventilation Slots
slot_width = 2.0
slot_length = 24.0
slot_pitch = 4.5

for k in range(-3, 3):
    sx = k * slot_pitch
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 10.0, lid_z))
    slot = bpy.context.active_object
    slot.scale = (slot_width, slot_length, lid_h + 2.0)
    bpy.ops.object.transform_apply(scale=True)
    
    mod_slot = lid_obj.modifiers.new(name=f"Vent_Slot_{k}", type='BOOLEAN')
    mod_slot.operation = 'DIFFERENCE'
    mod_slot.object = slot
    bpy.ops.object.select_all(action='DESELECT')
    lid_obj.select_set(True)
    bpy.context.view_layer.objects.active = lid_obj
    bpy.ops.object.modifier_apply(modifier=f"Vent_Slot_{k}")
    bpy.data.objects.remove(slot, do_unlink=True)

# Potentiometer Tuning Hole (5.0mm diameter centered over LM2596)
bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=lid_h + 2.0, location=(lm_cx, lm_cy, lid_z))
pot_hole = bpy.context.active_object
mod_pot = lid_obj.modifiers.new(name="Pot_Hole", type='BOOLEAN')
mod_pot.operation = 'DIFFERENCE'
mod_pot.object = pot_hole
bpy.ops.object.select_all(action='DESELECT')
lid_obj.select_set(True)
bpy.context.view_layer.objects.active = lid_obj
bpy.ops.object.modifier_apply(modifier="Pot_Hole")
bpy.data.objects.remove(pot_hole, do_unlink=True)

# ---------------------------------------------------------
# 5. Color-Coded 3D Component Mockups with Screw Holes & Screws
# ---------------------------------------------------------
pcb_z_top = floor_t + standoff_h + 2.0  # Top surface of PCB (Z = 2 + 4 + 2 = 8.0mm)

def cut_pcb_screw_holes(pcb_obj, hole_coords, pcb_z_center, pcb_thickness=2.0, hole_radius=1.5):
    for idx, (hx, hy) in enumerate(hole_coords):
        bpy.ops.mesh.primitive_cylinder_add(radius=hole_radius, depth=pcb_thickness + 1.0, location=(hx, hy, pcb_z_center))
        cutter = bpy.context.active_object
        
        mod = pcb_obj.modifiers.new(name=f"Screw_Hole_{idx+1}", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        bpy.ops.object.select_all(action='DESELECT')
        pcb_obj.select_set(True)
        bpy.context.view_layer.objects.active = pcb_obj
        bpy.ops.object.modifier_apply(modifier=f"Screw_Hole_{idx+1}")
        bpy.data.objects.remove(cutter, do_unlink=True)

# --- MAX3232 RS232 Module Mockup (Teal PCB) ---
max_pcb_z = floor_t + standoff_h + 1.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(max_cx, max_cy, max_pcb_z))
m_max = bpy.context.active_object
m_max.name = "Mockup_MAX3232_PCB"
m_max.scale = (32.0, 33.0, 2.0)
bpy.ops.object.transform_apply(scale=True)
m_max.data.materials.append(mat_max3232)

cut_pcb_screw_holes(m_max, max_coords, max_pcb_z)
for idx, (mx, my) in enumerate(max_coords):
    create_m3_screw(f"Screw_MAX3232_{idx+1}", mx, my, pcb_z_top, shaft_len=6.0)

# DB9 Connector block mockup (Metallic Silver)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(max_cx, -outer_w/2.0 + 5.5, floor_t + 4.0 + 7.5))
m_db9 = bpy.context.active_object
m_db9.name = "Mockup_DB9_Header"
m_db9.scale = (31.0, 11.0, 15.0)
bpy.ops.object.transform_apply(scale=True)
m_db9.data.materials.append(mat_db9_header)

# --- LM2596 Buck Converter Mockup (Royal Blue PCB) ---
lm_pcb_z = floor_t + standoff_h + 1.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lm_cx, lm_cy, lm_pcb_z))
m_lm = bpy.context.active_object
m_lm.name = "Mockup_LM2596_PCB"
m_lm.scale = (43.2, 21.6, 2.0)
bpy.ops.object.transform_apply(scale=True)
m_lm.data.materials.append(mat_lm2596)

cut_pcb_screw_holes(m_lm, lm_coords, lm_pcb_z)
for idx, (lx, ly) in enumerate(lm_coords):
    create_m3_screw(f"Screw_LM2596_{idx+1}", lx, ly, pcb_z_top, shaft_len=6.0)

# --- ESP32 DevKit V1 Board Mockup (Matte Black PCB) ---
esp_pcb_z = floor_t + standoff_h + 1.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(esp_cx, esp_cy, esp_pcb_z))
m_esp = bpy.context.active_object
m_esp.name = "Mockup_ESP32_PCB"
m_esp.scale = (28.5, 51.5, 2.0)
bpy.ops.object.transform_apply(scale=True)
m_esp.data.materials.append(mat_esp32)

cut_pcb_screw_holes(m_esp, esp_coords, esp_pcb_z)
for idx, (ex, ey) in enumerate(esp_coords):
    create_m3_screw(f"Screw_ESP32_{idx+1}", ex, ey, pcb_z_top, shaft_len=6.0)

bpy.ops.object.select_all(action='DESELECT')

result = {
    "status": "success",
    "message": "Enclosure generated with non-overlapping module layout, 3D PCB screw holes, internal standoffs, and 14x M3 mounting screws.",
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
