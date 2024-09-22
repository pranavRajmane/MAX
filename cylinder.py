import gmsh

gmsh.initialize()
gmsh.clear()
gmsh.model.add("model_name")


global_mesh_size = 0.1  # Adjust this value to change the mesh size
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", global_mesh_size)

Centre_x = 
Centre_y = float(input("enter y coordinate for centre: "))
Centre_z = float(input("enter z coordinate for centre: "))
radius = float(input("enter radius: "))


circle = gmsh.model.occ.addCircle(Centre_x, Centre_y, Centre_z, radius)

# Create a curve loop from the circle
curve_loop = gmsh.model.occ.addCurveLoop([circle])

# Create the surface using the curve loop
surface = gmsh.model.occ.addPlaneSurface([curve_loop])

gmsh.model.occ.synchronize()

# Physical group for meshing of base
base_surf_pg = gmsh.model.addPhysicalGroup(2, [surface], tag=100, name="lower_surface")

# Actual extrusion
h = 1
subdivisions = [10]  # for meshing
extrusion = gmsh.model.occ.extrude([(2, surface)], 0, 0, h, numElements=subdivisions)

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


