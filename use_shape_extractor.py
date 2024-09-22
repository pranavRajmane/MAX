from shape_extractor import get_shape_properties
import gmsh

def main():
    print("Welcome to the Shape Properties Importer!")
    properties = get_shape_properties()
    
    shape, Centre_x, Centre_y, Centre_z, radius, height = properties
    
    print("\nImported shape properties:")
    print(f"Shape: {shape}")
    print(f"Center: ({Centre_x}, {Centre_y}, {Centre_z})")
    print(f"Radius: {radius}")
    if height is not None:
        print(f"Height: {height}")
    else:
        print("Height: Not applicable (sphere)")
    
    
    gmsh.initialize()
    gmsh.clear()
    gmsh.model.add("model_name")


    global_mesh_size = 0.1  # Adjust this value to change the mesh size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", global_mesh_size)




    circle = gmsh.model.occ.addCircle(Centre_x, Centre_y, Centre_z, radius)

    # Create a curve loop from the circle
    curve_loop = gmsh.model.occ.addCurveLoop([circle])

    # Create the surface using the curve loop
    surface = gmsh.model.occ.addPlaneSurface([curve_loop])

    gmsh.model.occ.synchronize()

    # Physical group for meshing of base
    base_surf_pg = gmsh.model.addPhysicalGroup(2, [surface], tag=100, name="lower_surface")

    # Actual extrusion

    subdivisions = [10]  # for meshing
    extrusion = gmsh.model.occ.extrude([(2, surface)], 0, 0, height, numElements=subdivisions)

    gmsh.model.occ.synchronize()

    # Adding physical groups
    volume = gmsh.model.addPhysicalGroup(3, [extrusion[1][1]], name="volume")
    lateral_surf = gmsh.model.addPhysicalGroup(2, [extrusion[2][1]], name="lateral_surface")
    upper_surf = gmsh.model.addPhysicalGroup(2, [extrusion[0][1]], name="upper_surface")

    # Meshing
    gmsh.model.mesh.generate(3)

    gmsh.write("cylinder.msh")
    gmsh.fltk.run()

    gmsh.finalize()

if __name__ == "__main__":
    main()