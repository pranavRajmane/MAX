import os
import numpy as np
import matplotlib.pyplot as plt
import gmsh
from shape_extractor import get_shape_properties
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
    
    # Save the mesh file in the mesh_dir
    mesh_file = os.path.join(mesh_dir, "cylinder.msh")
    gmsh.write(mesh_file)
    
    gmsh.finalize()
    
    return radius, height

def run_simulation(radius, height, base_dir):
    mesh_dir = os.path.join(base_dir, "mesh")
    sim_dir = os.path.join(base_dir, "simulation")
    
    os.makedirs(mesh_dir, exist_ok=True)
    os.makedirs(sim_dir, exist_ok=True)
    
    mesh_file = "cylinder.msh"
    
    simulation = elmer.Simulation()
    
    heat_solver = elmer.load_solver("HeatSolver", simulation)
    heat_solver.data["Equation"] = "Heat Equation"
    heat_solver.data["Procedure"] = "HeatSolve" 
    heat_solver.data["Variable"] = "Temperature"
    heat_solver.data["Exec Solver"] = "Always"
    heat_solver.data["Stabilize"] = True
    heat_solver.data["Bubbles"] = False
    heat_solver.data["Lumped Mass Matrix"] = False
    heat_solver.data["Optimize Bandwidth"] = True
    heat_solver.data["Steady State Convergence Tolerance"] = 1e-5
    heat_solver.data["Nonlinear System Convergence Tolerance"] = 1e-7
    heat_solver.data["Nonlinear System Max Iterations"] = 20
    heat_solver.data["Nonlinear System Newton After Iterations"] = 3
    heat_solver.data["Nonlinear System Newton After Tolerance"] = 1e-3
    heat_solver.data["Nonlinear System Relaxation Factor"] = 1
    
    copper = elmer.Material(simulation, "Copper")
    copper.data["Heat Conductivity"] = 401.0
    copper.data["Heat Capacity"] = 385.0
    copper.data["Density"] = 8960.0
    
    body = elmer.Body(simulation, "Cylinder", body_ids=[101])
    body.data["Material"] = copper.name
    body.data["Equation"] = 1
    body.data["Body Force"] = 1
    
    boundary_bottom = elmer.Boundary(simulation, "Bottom", geo_ids=[100])
    boundary_bottom.data["Temperature"] = 100.0
    
    boundary_top = elmer.Boundary(simulation, "Top", geo_ids=[103])
    boundary_top.data["Temperature"] = 0.0
    
    boundary_lateral = elmer.Boundary(simulation, "Lateral", geo_ids=[102])
    boundary_lateral.data["Heat Flux BC"] = True
    boundary_lateral.data["Heat Flux"] = 0.0
    
    equation = elmer.Equation(simulation, "HeatEquation", solvers=[heat_solver])
    
    flux_solver = elmer.Solver(simulation, "FluxSolver")
    flux_solver.data["Equation"] = "HeatFlux"
    flux_solver.data["Procedure"] = "FluxSolver" 
    flux_solver.data["Calculate Flux"] = True
    flux_solver.data["Target Variable"] = "Temperature"
    flux_solver.data["Flux Variable"] = "Heat Flux"
    flux_solver.data["Calculation Condition"] = "Always"
    
    simulation.write_sif(sim_dir)
    simulation.write_startinfo(sim_dir)
    
    execute.run_elmer_grid(mesh_dir, mesh_file, out_dir=sim_dir)
    execute.run_elmer_solver(sim_dir)
    
    print("Simulation completed successfully!")
    
    temp_data = post.dat_to_dataframe(os.path.join(sim_dir, "temperature.dat"))
    flux_data = post.dat_to_dataframe(os.path.join(sim_dir, "heat_flux.dat"))
    
    plt.figure(figsize=(10, 6))
    plt.plot(temp_data['Z']/height, temp_data['Temperature'], '-o')
    plt.title('Temperature Distribution along the Cylinder Height')
    plt.xlabel('Normalized Height')
    plt.ylabel('Temperature (K)')
    plt.grid(True)
    plt.savefig(os.path.join(sim_dir, 'temperature_distribution.png'))
    plt.close()
    
    plt.figure(figsize=(10, 6))
    flux_magnitude = np.sqrt(flux_data['Heat Flux 1']**2 + flux_data['Heat Flux 2']**2 + flux_data['Heat Flux 3']**2)
    plt.plot(flux_data['Z']/height, flux_magnitude, '-o')
    plt.title('Heat Flux Magnitude along the Cylinder Height')
    plt.xlabel('Normalized Height')
    plt.ylabel('Heat Flux Magnitude (W/m^2)')
    plt.grid(True)
    plt.savefig(os.path.join(sim_dir, 'heat_flux_distribution.png'))
    plt.close()
    
    print("Post-processing completed. Plots saved in the simulation directory.")
    
    errors, warnings, stats = post.scan_logfile(sim_dir)
    if errors:
        print("Errors found:")
        for error in errors:
            print(error)
    if warnings:
        print("Warnings found:")
        for warning in warnings:
            print(warning)
    
    print("Simulation statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")

def main():
    base_dir = "/Users/pranavrajmane/Desktop/ 3d_renderer"
    mesh_dir = os.path.join(base_dir, "mesh")
    os.makedirs(mesh_dir, exist_ok=True)
    
    radius, height = create_mesh(mesh_dir)
    run_simulation(radius, height, base_dir)

if __name__ == "__main__":
    main()