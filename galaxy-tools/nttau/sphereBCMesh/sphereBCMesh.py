import gmsh
import os
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument('file_path')
args = parser.parse_args()
file_path = args.file_path

# Open the file and load the data
with open(file_path, 'r') as file:
    data = json.load(file)

step_file = "reactor.step"

sphere_data = data['sphere_data']
num_layers = sphere_data['num_layers']
mesh_factor = sphere_data['mesh_factor']

j=1

geo=open('sphereboundaries.geo', 'w')
print('SetFactory("OpenCASCADE");',file=geo) #Add OpenCASCADE to .geo file
print('//+',file=geo)
print(f'Mesh.CharacteristicLengthFactor = {mesh_factor};',file=geo) #Sets Mesh factor in .geo file
print('//+',file=geo)
print(f'Merge "{step_file}";', file=geo) #Merges input STEP file
print('//+', file=geo)

for i in range (1, num_layers+1): #loops setting the physical volumes of the spheres
    print(f'Physical Volume("sph_{i}_volume", {i}) = {{{i}}};', file=geo)
    print('//+',file=geo)

for i in range (1, num_layers+1): #loops setting the physical surfaces for meshing where i corresponds to the cylindrical layer
    sphere_tag = (i*2) - 1  #wall is the long length of cylinder
    plane_tag = i*2 #top circular face
    if i <= 2:
        print(f'Physical Surface("sph_{i}_sphere", {sphere_tag}) = {{{sphere_tag}}};', file=geo)
        print('//+',file=geo)
        print(f'Physical Surface("sph_{i}_plane", {plane_tag}) = {{{plane_tag}}};', file=geo)
        print('//+',file=geo)
        
    if i >= 3:
        print(f'Physical Surface("sph_{i}_sphere", {sphere_tag}) = {{{3*(i-1)}}};', file=geo)
        print('//+',file=geo)
        print(f'Physical Surface("sph_{i}_plane", {plane_tag}) = {{{3*(i-1) + 1}}};', file=geo)
        print('//+',file=geo)

# 3D Meshing Commands
print('Mesh.Algorithm = 1;', file=geo)  # Sets meshing algorithm (1: Delaunay, 2: Frontal, etc.)
print('Mesh.Algorithm3D = 1;', file=geo)  # Sets 3D meshing algorithm
print('Mesh 3;', file=geo)  # Instructs Gmsh to generate 3D mesh

geo.close()

os.rename("sphereboundaries.geo", "outputfile.geo")

gmsh.write("output.msh")

os.rename("output.msh", "outputfile.msh")



