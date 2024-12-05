import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# File paths
input_stl_path = "hullDTC.stl"  # Replace with the path to your input STL file
output_stl_path = "hullDTC_underwater.stl"  # Replace with the path to your output STL file

# Import the STL file
bpy.ops.wm.stl_import(filepath=input_stl_path)
obj = bpy.context.selected_objects[0]  # Reference to the imported object

# Ensure the object is selected
bpy.context.view_layer.objects.active = obj
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

# Switch to Edit Mode
bpy.ops.object.mode_set(mode='EDIT')

# Select all geometry
bpy.ops.mesh.select_all(action='SELECT')

# Perform the bisect operation
bpy.ops.mesh.bisect(
    plane_co=(0, 0, 0.244),    # Point on the Z-plane (origin)
    plane_no=(0, 0, 1),    # Normal vector of the plane (along Z-axis)
    use_fill=True,         # Fill the cut plane
    clear_inner=False,     # Keep the lower part
    clear_outer=True       # Remove the upper part
)

# Return to Object Mode
bpy.ops.object.mode_set(mode='OBJECT')

# Export the modified object as an STL file
bpy.ops.wm.stl_export(filepath=output_stl_path)

print(f"Modified STL exported to {output_stl_path}")
