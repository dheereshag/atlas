# /// script
# dependencies = []
# ///
import socket
import json
import sys

# Python code to be executed inside Blender main thread
BLENDER_CLEAR_SCRIPT = """
import bpy

# Select all objects in the scene
bpy.ops.object.select_all(action='SELECT')

# Delete selected objects
bpy.ops.object.delete(use_global=False)

# Clean up orphaned data blocks (meshes, materials, lights, cameras)
for mesh in bpy.data.meshes:
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

for mat in bpy.data.materials:
    if mat.users == 0:
        bpy.data.materials.remove(mat)

result = {
    "status": "success",
    "message": "Entire canvas cleared successfully.",
    "remaining_objects_count": len(bpy.data.objects)
}
"""

def clear_blender_canvas(host: str = "127.0.0.1", port: int = 9876):
    """Sends a request to the Blender MCP server to clear the scene."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            
            payload = json.dumps({
                "type": "execute",
                "code": BLENDER_CLEAR_SCRIPT,
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
            print("Blender Server Response:")
            print(json.dumps(response, indent=2))
            
    except ConnectionRefusedError:
        print(f"Error: Could not connect to Blender server at {host}:{port}.")
        print("Please make sure Blender is open and the MCP server is running.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clear_blender_canvas()
