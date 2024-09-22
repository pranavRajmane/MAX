import sys
import json
from shape_extractor import get_shape_properties
import gmsh

def main():
    print("Welcome to the Shape Properties Importer!", flush=True)
    print("Please enter the shape data:", flush=True)
    
    shape_data = input()
    properties = get_shape_properties()
    
    shape, Centre_x, Centre_y, Centre_z, radius, height = properties
    
    print(f"\nImported shape properties:", flush=True)
    print(f"Shape: {shape}", flush=True)
    print(f"Center: ({Centre_x}, {Centre_y}, {Centre_z})", flush=True)
    print(f"Radius: {radius}", flush=True)
    if height is not None:
        print(f"Height: {height}", flush=True)
    else:
        print("Height: Not applicable (sphere)", flush=True)
    
    print("\nDo you want to proceed with the Gmsh simulation? (yes/no)", flush=True)
    response = input().lower()
    
    if response != 'yes':
        print("Simulation cancelled.", flush=True)
        return
    
    gmsh.initialize()
    gmsh.clear()
    gmsh.model.add("model_name")
    global_mesh_size = 0.1
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", global_mesh_size)
    circle = gmsh.model.occ.addCircle(Centre_x, Centre_y, Centre_z, radius)
    curve_loop = gmsh.model.occ.addCurveLoop([circle])
    surface = gmsh.model.occ.addPlaneSurface([curve_loop])
    gmsh.model.occ.synchronize()
    base_surf_pg = gmsh.model.addPhysicalGroup(2, [surface], tag=100, name="lower_surface")
    subdivisions = [10]
    extrusion = gmsh.model.occ.extrude([(2, surface)], 0, 0, height, numElements=subdivisions)
    gmsh.model.occ.synchronize()
    volume = gmsh.model.addPhysicalGroup(3, [extrusion[1][1]], name="volume")
    lateral_surf = gmsh.model.addPhysicalGroup(2, [extrusion[2][1]], name="lateral_surface")
    upper_surf = gmsh.model.addPhysicalGroup(2, [extrusion[0][1]], name="upper_surface")
    gmsh.model.mesh.generate(3)
    
    nodes, elements = get_mesh_data()
    mesh_data = {
        "nodes": nodes,
        "elements": elements
    }
    print("MESH_DATA:" + json.dumps(mesh_data), flush=True)
    
    gmsh.finalize()

def get_mesh_data():
    nodes = []
    elements = []
    
    # Get nodes
    node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
    for i in range(len(node_tags)):
        nodes.append({
            "tag": int(node_tags[i]),
            "x": node_coords[3*i],
            "y": node_coords[3*i+1],
            "z": node_coords[3*i+2]
        })
    
    # Get elements
    element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements()
    for i in range(len(element_types)):
        for j in range(len(element_tags[i])):
            elements.append({
                "type": int(element_types[i]),
                "tag": int(element_tags[i][j]),
                "nodes": [int(tag) for tag in element_node_tags[i][j*gmsh.model.mesh.getElementProperties(element_types[i])[3]:
                                                                 (j+1)*gmsh.model.mesh.getElementProperties(element_types[i])[3]]]
            })
    
    return nodes, elements

if __name__ == "__main__":
    main()
