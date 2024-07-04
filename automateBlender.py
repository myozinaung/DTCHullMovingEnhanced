# Calculate Mass, Inertia, and Center of Buoyancy/Gravity of a Submerged Hull in Blender
# Values are calculated for a half hull geometry
# Input: hull_clipped.stl, Length(for kyy & kzz), Beam (for kxx), rho_water
# Output: Mass, Inertia, and CoB/CoG
# Usage: "C:\Program Files\Blender Foundation\Blender 2.93\blender.exe" --background --python automateBlender.py -- --stl_filepath hull_clipped.stl --draft 0.244 --rho_water 998.2
# Usage: python3 automateBlender.py --stl_filepath hullDTC.stl --draft 0.244 --rho_water 1000
# Steps:
# 1. Import STL hull geometry
# 2. Get the dimensions and bounding box of the hull
# 3. Bisect the hull at the draft
# 4. Made the clipped hull manifold (using 3D Print Toolbox)
# 5. Calculated the volume of the clipped hull
# 6. Set the origin to the center of mass (volume) >> get the CoG as Transform X, Y, Z

# pip install bpy
import bpy
import bmesh
import argparse

def calculate_hull_properties(stl_filepath, draft, rho_water):
    # Open a new blank file (without default cube and camera)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Ensure the 3D Print Toolbox is enabled (for making manifold)
    if not bpy.context.preferences.addons.get('object_print3d_utils'):
        bpy.ops.preferences.addon_enable(module='object_print3d_utils')

    # Import the STL file
    bpy.ops.import_mesh.stl(filepath=stl_filepath)

    # Assuming the imported mesh is the only object in the scene
    obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = obj

    ### Get the dimensions of the hull ###
    # Get the dimensions of the hull
    dim = obj.dimensions
    print(f"Dimensions: {dim}")
    Length = dim[0] * 0.94  # Length of the hull, LPP = 94% of the LOA
    Beam   = dim[1]  # Beam of the hull
    Depth  = dim[2]  # Depth of the hull
    VCG    = Depth * 0.65  # Vertical Center of Gravity (VCG), Use the formulae for different types of vessels

    # Get the bounding box of the hull
    bbox = obj.bound_box
    print(f"Bounding Box Min: {bbox[0][0]:.4f}, {bbox[0][1]:.4f}, {bbox[0][2]:.4f}")
    print(f"Bounding Box Max: {bbox[6][0]:.4f}, {bbox[6][1]:.4f}, {bbox[6][2]:.4f}")
    # Write bounds to file
    with open('hullBounds.txt', 'w') as f:
        f.write(f"hullXmin  {bbox[0][0]:.4f};\n")
        f.write(f"hullXmax  {bbox[6][0]:.4f};\n")
        f.write(f"hullYmin  {bbox[0][1]:.4f};\n")
        f.write(f"hullYmax  {bbox[6][1]:.4f};\n")
        f.write(f"hullZmin  {bbox[0][2]:.4f};\n")
        f.write(f"hullZmax  {bbox[6][2]:.4f};\n")
        f.write(f"zWL       {draft:.4f};\n")
    print(f"Results written to hullBounds.txt")

    ### Clip the hull: Bisect the mesh at the draft ###
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # Create a bmesh object from the mesh
    bm = bmesh.from_edit_mesh(obj.data)

    # Bisect the mesh using the z-plane
    bpy.ops.mesh.bisect(
        plane_co=(0, 0, draft),
        plane_no=(0, 0, 1),
        use_fill=False,
        clear_outer=True
    )
    # Update the mesh and exit edit mode
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')


    ### Make manifold and calculate volume ###
    # Ensure we have the object selected
    obj = bpy.context.selected_objects[0]

    # Make Manifold using 3D Print Toolbox
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.print3d_clean_non_manifold()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Calculate the volume of the object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vol = bm.calc_volume()
    bm.free()

    ### Get the Center of Volume ###
    # Set Origin to Center of Mass (Volume)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
    # Get the Transform X, Y, Z
    transform_x = obj.location.x
    transform_y = obj.location.y
    transform_z = obj.location.z

    # Calculate mass, inertia, and moments
    mass = vol * rho_water / 2  # mass of half hull

    kxx = 0.34 * Beam
    kyy = 0.25 * Length
    kzz = 0.26 * Length

    Ixx = mass * kxx**2
    Iyy = mass * kyy**2
    Izz = mass * kzz**2

    print(f"Mass: {mass:.4f}")
    print(f"Ixx: {Ixx:.4f}, Iyy: {Iyy:.4f}, Izz: {Izz:.4f}")
    print(f"CoB X: {transform_x:.4f}, Y: {transform_y:.4f}, Z: {transform_z:.4f}")
    print(f"CoG X: {transform_x:.4f}, Y: {0}, Z: {VCG:.4f}")
    # Write results to file
    with open("hullMassInertiaCoG.txt", "w") as f:
        f.write(f"mass            {mass:.2f};   // [kg]\n")
        f.write(f"Ixx             {Ixx:.2f};       // [kg.m^2] for Roll motion (not important here)\n")
        f.write(f"Iyy             {Iyy:.2f};      // [kg.m^2] for Pitch motion\n")
        f.write(f"Izz             {Izz:.2f};      // [kg.m^2] for Yaw motion (not important here)\n")
        f.write(f"centreOfMass    ({transform_x:.6f} {0} {VCG:.6f}); // [m] (x y z), (LCB 0 VCG)\n")
    print(f"Results written to hullMassInertiaCoG.txt")

if __name__ == "__main__":
    # Argument parser for input arguments
    parser = argparse.ArgumentParser(description="Calculate hull properties")
    parser.add_argument("--stl_filepath", type=str, required=True, help="Path to the STL file")
    parser.add_argument("--draft", type=float, required=True, help="Draft of the hull")
    parser.add_argument("--rho_water", type=float, default=1000, help="Density of water in kg/m^3")

    args = parser.parse_args()

    calculate_hull_properties(args.stl_filepath, args.draft, args.rho_water)


