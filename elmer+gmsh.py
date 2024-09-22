import os
from shape_extractor import get_shape_properties
import gmsh
from pyelmer import elmer, execute, post

def create_mesh(mesh_dir):
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
    gmsh.model.add("cylinder_model")
    
    global_mesh_size = 0.1  # Adjust this value to change the mesh size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", global_mesh_size)
    
    circle = gmsh.model.occ.addCircle(Centre_x, Centre_y, Centre_z, radius)
    curve_loop = gmsh.model.occ.addCurveLoop([circle])
    surface = gmsh.model.occ.addPlaneSurface([curve_loop])
    gmsh.model.occ.synchronize()
    
    base_surf_pg = gmsh.model.addPhysicalGroup(2, [surface], tag=100, name="lower_surface")
    
    subdivisions = [10]  # for meshing
    extrusion = gmsh.model.occ.extrude([(2, surface)], 0, 0, height, numElements=subdivisions)
    gmsh.model.occ.synchronize()
    
    volume = gmsh.model.addPhysicalGroup(3, [extrusion[1][1]], tag=101, name="volume")
    lateral_surf = gmsh.model.addPhysicalGroup(2, [extrusion[2][1]], tag=102, name="lateral_surface")
    upper_surf = gmsh.model.addPhysicalGroup(2, [extrusion[0][1]], tag=103, name="upper_surface")
    
    gmsh.model.mesh.generate(3)
    gmsh.write(os.path.join(mesh_dir, "cylinder.msh"))
    gmsh.finalize()
    
    return 100, 102, 103, 101  # Return tags instead of GMSH objects

def run_simulation(base_surf_tag, lateral_surf_tag, upper_surf_tag, volume_tag, sim_dir):
    sim = elmer.Simulation()
    sim.settings = {"Coordinate System": "Cartesian 3D", "Simulation Type": "Steady state"}
    
    copper = elmer.Material(sim, "Copper")
    copper.data["Heat Conductivity"] = 401.0
    copper.data["Heat Capacity"] = 385.0
    copper.data["Density"] = 8960.0
    
    solver_heat = elmer.Solver(sim, "heat_solver")
    solver_heat.data = {
        "Equation": "HeatSolver",
        "Procedure": '"HeatSolve" "HeatSolver"',
        "Variable": '"Temperature"',
        "Variable Dofs": 1,
    }
    
    solver_output = elmer.Solver(sim, "output_solver")
    solver_output.data = {
        "Exec Solver": "After timestep",
        "Equation": "ResultOutputSolver",
        "Procedure": '"ResultOutputSolve" "ResultOutputSolver"',
    }
    
    eqn = elmer.Equation(sim, "main", [solver_heat])
    T0 = elmer.InitialCondition(sim, "T0", {"Temperature": 273.15})
    
    bdy_cylinder = elmer.Body(sim, "cylinder", [volume_tag])
    bdy_cylinder.material = copper
    bdy_cylinder.initial_condition = T0
    bdy_cylinder.equation = eqn
    
    bndry_bottom = elmer.Boundary(sim, "bottom", [base_surf_tag])
    bndry_bottom.data["Temperature"] = 353.15  # 80 °C
    
    bndry_top = elmer.Boundary(sim, "top", [upper_surf_tag])
    bndry_top.data["Temperature"] = 293.15  # 20 °C
    
    bndry_lateral = elmer.Boundary(sim, "lateral", [lateral_surf_tag])
    bndry_lateral.data["Temperature"] = 293.15  # 20 °C
    
    sim.write_startinfo(sim_dir)
    sim.write_sif(sim_dir)
    
    # Execute ElmerGrid & ElmerSolver
    execute.run_elmer_grid(sim_dir, "cylinder.msh")
    execute.run_elmer_solver(sim_dir)
    
    # Scan log for errors and warnings
    err, warn, stats = post.scan_logfile(sim_dir)
    print("Errors:", err)
    print("Warnings:", warn)
    print("Statistics:", stats)

def main():
    sim_dir = "/Users/pranavrajmane/Desktop/3d_renderer"
    os.makedirs(sim_dir, exist_ok=True)
    
    base_surf_tag, lateral_surf_tag, upper_surf_tag, volume_tag = create_mesh(sim_dir)
    run_simulation(base_surf_tag, lateral_surf_tag, upper_surf_tag, volume_tag, sim_dir)

if __name__ == "__main__":
    main()
