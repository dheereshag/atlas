# /// script
# dependencies = []
# ///
"""
Custom 3D Printed Desktop Enclosure Generator for Blender (bpy)
Generates an enclosure base, ventilated lid, mounting standoffs, port cutouts,
and 3D visual component mockups for:
1. LM2596 DC-DC Buck Converter
2. MAX3232 RS232 Module
3. ESP32 DevKit V1 Board
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
# Materials Setup
# ---------------------------------------------------------
def get_or_create_material(name, color, roughness=0.4):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Roughness'].default_value = roughness
    return mat

mat_enclosure = get_or_create_material("Enclosure_ABS", (0.12, 0.14, 0.18, 1.0), 0.3)
mat_lid = get_or_create_material("Enclosure_Lid", (0.18, 0.20, 0.25, 1.0), 0.3)
mat_pcb_blue = get_or_create_material("PCB_Blue", (0.05, 0.25, 0.70, 1.0), 0.2)
mat_pcb_black = get_or_create_material("PCB_Black", (0.02, 0.02, 0.02, 1.0), 0.2)
mat_metal = get_or_create_material("Metal_DB9", (0.7, 0.7, 0.75, 1.0), 0.1)

# ---------------------------------------------------------
# Enclosure Specs (in mm)
# ---------------------------------------------------------
outer_l = 90.0   # X-axis length
outer_w = 70.0   # Y-axis width
outer_h = 24.0   # Z-axis height
wall_t = 2.0     # Wall thickness
floor_t = 2.0    # Floor thickness

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
base_obj.data.materials.append(mat_enclosure)

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
    post.data.materials.append(mat_enclosure)
    
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

# LM2596 PCB Mounting Standoffs (2x M3 diagonal)
lm_cx, lm_cy = -20.0, 14.0
lm_standoff_dx, lm_standoff_dy = 18.0, 10.0
lm_coords = [
    (lm_cx - lm_standoff_dx, lm_cy - lm_standoff_dy),
    (lm_cx + lm_standoff_dx, lm_cy + lm_standoff_dy)
]
for i, (lx, ly) in enumerate(lm_coords):
    bpy.ops.mesh.primitive_cylinder_add(radius=3.0, depth=4.0, location=(lx, ly, floor_t + 2.0))
    lm_post = bpy.context.active_object
    lm_post.name = f"LM2596_Standoff_{i+1}"
    lm_post.data.materials.append(mat_enclosure)
    
    mod = base_obj.modifiers.new(name=f"Join_LM_Post_{i+1}", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = lm_post
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier=f"Join_LM_Post_{i+1}")
    bpy.data.objects.remove(lm_post, do_unlink=True)

# ---------------------------------------------------------
# 3. Port Cutouts (DB9 Front & Micro-USB Side)
# ---------------------------------------------------------
# DB9 Cutout on Front Wall
db9_w, db9_h = 31.5, 15.5
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -outer_w / 2.0, floor_t + 4.0 + db9_h / 2.0))
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

# Micro-USB Cutout on Right Side Wall
usb_w, usb_h = 10.5, 7.5
usb_y_pos = 5.0
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
# 4. Ventilated Top Lid
# ---------------------------------------------------------
lid_h = 2.5
lid_z = outer_h + lid_h / 2.0 + 5.0  # Displayed 5mm above base

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, lid_z))
lid_obj = bpy.context.active_object
lid_obj.name = "Enclosure_Top_Lid"
lid_obj.scale = (outer_l, outer_w, lid_h)
bpy.ops.object.transform_apply(scale=True)
lid_obj.data.materials.append(mat_lid)

# 4x Lid Corner Screw Holes
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

# Potentiometer Tuning Hole (5.0mm diameter)
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
# 5. 3D Component Mockups
# ---------------------------------------------------------
# MAX3232 RS232 Module Mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -outer_w/2.0 + 16.5, floor_t + 4.0 + 1.0))
m_max = bpy.context.active_object
m_max.name = "Mockup_MAX3232_PCB"
m_max.scale = (32.0, 33.0, 2.0)
bpy.ops.object.transform_apply(scale=True)
m_max.data.materials.append(mat_pcb_blue)

# DB9 Connector block mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -outer_w/2.0 + 5.5, floor_t + 4.0 + 7.5))
m_db9 = bpy.context.active_object
m_db9.name = "Mockup_DB9_Header"
m_db9.scale = (31.0, 11.0, 15.0)
bpy.ops.object.transform_apply(scale=True)
m_db9.data.materials.append(mat_metal)

# LM2596 Buck Converter Mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lm_cx, lm_cy, floor_t + 4.0 + 1.0))
m_lm = bpy.context.active_object
m_lm.name = "Mockup_LM2596_PCB"
m_lm.scale = (43.2, 21.6, 2.0)
bpy.ops.object.transform_apply(scale=True)
m_lm.data.materials.append(mat_pcb_blue)

# ESP32 DevKit V1 Board Mockup
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(18.0, 5.0, floor_t + 4.0 + 1.0))
m_esp = bpy.context.active_object
m_esp.name = "Mockup_ESP32_PCB"
m_esp.scale = (28.5, 51.5, 2.0)
bpy.ops.object.transform_apply(scale=True)
m_esp.data.materials.append(mat_pcb_black)

bpy.ops.object.select_all(action='DESELECT')

result = {
    "status": "success",
    "message": "Reverted back to clean 6-object enclosure setup.",
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
