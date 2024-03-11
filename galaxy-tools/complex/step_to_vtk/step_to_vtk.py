import gmsh
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("Output_Filename")

args = parser.parse_args()

output_file = args.Output_Filename

# Initialize Gmsh
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("modelo_1")


# Load the STEP file
gmsh.merge("geometry.step")

# # Set meshing options
# gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_settings["mesh_max_size"])
# gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_settings["mesh_min_size"])

# Generate the mesh
gmsh.model.mesh.generate(3)

# Save the mesh
gmsh.write("mesh.vtk")
os.rename("mesh.vtk","output_file.vtk")