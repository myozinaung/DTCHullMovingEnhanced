# Create a Watertight Hull (Solid STL) using Surface STL file
# pip install bpy
import bpy
import bmesh
import argparse

def calculate_hull_properties(stl_filepath, scale_factor):
    # Open a new blank file (without default cube and camera)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Ensure the 3D Print Toolbox is enabled (for making manifold)
    if not bpy.context.preferences.addons.get('object_print3d_utils'):
        bpy.ops.preferences.addon_enable(module='object_print3d_utils')

    # Import the STL file
    bpy.ops.import_mesh.stl(filepath=stl_filepath)

    ### Make manifold and calculate volume ###
    # Ensure we have the object selected
    obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = obj

    # Make Manifold using 3D Print Toolbox    
    # bpy.ops.mesh.print3d_check_all()
    bpy.ops.mesh.print3d_clean_non_manifold()
    bpy.ops.mesh.print3d_clean_distorted()
    bpy.ops.mesh.print3d_clean_non_manifold()
    bpy.ops.mesh.print3d_clean_distorted()
    bpy.ops.mesh.print3d_clean_non_manifold()
    bpy.ops.mesh.print3d_clean_distorted()
    
    # Transform by scale_factor
    # scale_factor = 1/31.599 # KCS
    scale_factor = 1/scale_factor
    bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))

    bpy.ops.mesh.print3d_export()

if __name__ == "__main__":
    # Argument parser for input arguments
    parser = argparse.ArgumentParser(description="Calculate hull properties")
    parser.add_argument("stl_filepath", type=str, help="Path to the STL file")
    parser.add_argument("--scale_factor", type=float, default=1, help="Scale factor for the STL file")

    args = parser.parse_args()

    calculate_hull_properties(args.stl_filepath, args.scale_factor)


