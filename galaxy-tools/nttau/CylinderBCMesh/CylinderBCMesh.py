import gmsh
import argparse
import json
import os

def create_geometry_and_mesh(cylinder_data):
    gmsh.initialize()
    gmsh.model.add("cylinder_model")

    step_file = "reactor.step"
    num_layers = cylinder_data['num_layers']
    mesh_factor = cylinder_data['mesh_factor']

    gmsh.option.setNumber("Mesh.CharacteristicLengthFactor", mesh_factor)
    gmsh.option.setNumber("Mesh.Algorithm", 1)  # Delaunay
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # 3D algorithm

    # Import STEP file
    gmsh.model.occ.importShapes(step_file)

    # Synchronize necessary due to use of OpenCASCADE
    gmsh.model.occ.synchronize()

    j = 1  # Initial tag offset

    # Creating physical groups for surfaces
    for i in range(1, num_layers + 1):
        wall_tag = i * 3 - 2  # Wall is the long length of cylinder
        top_tag = i * 3 - 1   # Top circular face
        bottom_tag = i * 3    # Bottom circular face

        if i <= 2:
            gmsh.model.addPhysicalGroup(2, [wall_tag], wall_tag)
            gmsh.model.setPhysicalName(2, wall_tag, f"cyl_{i}_wall")
            gmsh.model.addPhysicalGroup(2, [top_tag], top_tag)
            gmsh.model.setPhysicalName(2, top_tag, f"cyl_{i}_top")
            gmsh.model.addPhysicalGroup(2, [bottom_tag], bottom_tag)
            gmsh.model.setPhysicalName(2, bottom_tag, f"cyl_{i}_bottom")
        else:
            gmsh.model.addPhysicalGroup(2, [wall_tag + j], wall_tag + j)
            gmsh.model.setPhysicalName(2, wall_tag + j, f"cyl_{i}_wall")
            gmsh.model.addPhysicalGroup(2, [top_tag + j], top_tag + j)
            gmsh.model.setPhysicalName(2, top_tag + j, f"cyl_{i}_top")
            gmsh.model.addPhysicalGroup(2, [bottom_tag + j], bottom_tag + j)
            gmsh.model.setPhysicalName(2, bottom_tag + j, f"cyl_{i}_bottom")
            j += 1

    for i in range(1, num_layers + 1):
        volume_tag = i
        gmsh.model.addPhysicalGroup(3, [volume_tag], tag=30 + i)
        gmsh.model.setPhysicalName(3, 30 + i, f"cyl_{i}_volume")

    # Generate mesh
    gmsh.model.mesh.generate(3)

    # Save mesh (optional, uncomment to save)
    gmsh.write("meshed_model.msh")

    gmsh.finalize()

# Main script
parser = argparse.ArgumentParser()
parser.add_argument('file_path')
args = parser.parse_args()
file_path = args.file_path

with open(file_path, 'r') as file:
    data = json.load(file)

cylinder_data = data['cylinder_data']
create_geometry_and_mesh(cylinder_data)


os.rename("meshed_model.msh", "outputfile.msh")
