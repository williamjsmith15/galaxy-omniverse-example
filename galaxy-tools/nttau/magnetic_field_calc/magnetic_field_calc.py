import array
from MagCoil import MagCoil
import numpy as np
import math
from pylab import *
import time
import csv

# 1. Import Bounding Box and dx dy and dz
# 2. Load in PF coil csv
import argparse
import json


def loop_field(geom_type,pf_coil_datafile_path, bounding_box_filepath, dx, dy, dz):
    geom_type = "Torus"
    #Set file names to write values to 
    start_time = time.perf_counter()
    grid_file = bounding_box_filepath
    grid_vals_str = [] 
    if geom_type =="Cylinder": 

        B_file= open("B_multi.csv", "w")
        filename = open(pf_coil_datafile_path, 'r')
        file = csv.DictReader(filename)

    elif geom_type =="Torus": 

        
        B_file =open("PF_B.csv", 'w')

        filename = open(pf_coil_datafile_path, 'r')
        file = csv.DictReader(filename)

    else:
        print("invalid geometry type given") 


    with open(bounding_box_filepath, 'r') as grid_file:
        reader = csv.reader(grid_file)
        next(reader)  # Skip the header row

        # Read the Min values
        min_row = next(reader)
        x_min, y_min, z_min = map(float, min_row[1:])

        # Read the Max values
        max_row = next(reader)
        x_max, y_max, z_max = map(float, max_row[1:])

    # Now you have x_min, x_max, y_min, y_max, z_min, z_max with the correct values

    x_points=1+((x_max-x_min)/dx)
    y_points=1+((y_max-y_min)/dy)
    z_points=1+((z_max-z_min)/dz)

    coords_total = int((x_points)*(y_points)*(z_points))
    print('coords_total =',coords_total)

    print(x_min,x_max,dx,y_min,y_max,dy,z_min,z_max,dz)

 
# creating empty lists to write to later
    Nr_str = []
    Nz_str = []
    I_str= []
    r_str = []
    dr_str = []
    coil_dz_str = []
    x_centre_str = []
    y_centre_str = []
    z_centre_str = []
    x_normal_str = []
    y_normal_str = []
    z_normal_str = []

    coil_counter =0
    for col in file:

        #count number of coils
        coil_counter=coil_counter+1

        #Read in values
        Nr_str.append(col['R_turns'])
        Nz_str.append(col['R_turns'])
        I_str.append(col['I'])
        r_str.append(col['r_av'])
        dr_str.append(col['dr'])
        coil_dz_str.append(col['dr'])
        x_centre_str.append(col['coil_x'])
        y_centre_str.append(col['coil_y'])
        z_centre_str.append(col['coil_z'])
        x_normal_str.append(col['normal_z'])
        y_normal_str.append(col['normal_y'])
        z_normal_str.append(col['normal_x'])

    coil_num=coil_counter
    print("number of coils = ", coil_num)
    count=0

    #Create correct size arrays to store info about each coil
    Nr = np.zeros(coil_num)
    Nz = np.zeros(coil_num)
    N = np.zeros(coil_num)
    I= np.zeros(coil_num)
    r = np.zeros(coil_num)
    dr = np.zeros(coil_num)
    coil_dz = np.zeros(coil_num)
    x_centre = np.zeros(coil_num)
    y_centre = np.zeros(coil_num)
    z_centre = np.zeros(coil_num)
    x_normal = np.zeros(coil_num)
    y_normal = np.zeros(coil_num)
    z_normal = np.zeros(coil_num)

# convert to correct type (integer/float)

    while count<= coil_num-1:
   
        Nr[count]=int(Nr_str[count]) 
        Nz[count]=int(Nz_str[count]) 
        N[count]=int((Nz[count]*Nr[count])) 
        I[count]=float(I_str[count])
        r[count]=float(r_str[count])
        dr[count]=float(dr_str[count])
        coil_dz[count]=float(coil_dz_str[count])
        x_centre[count]=float(x_centre_str[count])
        y_centre[count]=float(y_centre_str[count])
        z_centre[count]=float(z_centre_str[count])
        x_normal[count]=float(x_normal_str[count])
        y_normal[count]=float(y_normal_str[count])
        z_normal[count]=float(z_normal_str[count])

 #   print(N[count],I[count],N[count]*I[count])

        count=count+1

    print ("All coils identified")


#Sampling points 
#Creates grid of x_points by y points by z points 


    count=0

    print ("All coils created")

    #Create arrays to store the field from the current coil and total field
    field=np.zeros((coords_total,6))
    total_field=np.zeros((coords_total,7))

# Calculates the magnetic field from one coil using its properties
    def Field_Calc(N_val,I_val,R_I,R_av,x_c,y_c,z_c,x_n,y_n,z_n): 
 
        coil_centre = array([x_c,y_c,z_c]) # coil centre 
        coil_normal = array([x_n,y_n,z_n]) # normal vector to plane of coil 

   # print(coil_centre) 
   # print(coil_normal)

        #Define coil 
        c1=MagCoil(coil_centre, coil_normal, R=R_av, I=N_val*I_val) 
        print(N_val*I_val)

        #Use to define centre point of grid 
        centre=MagCoil(array([0.0,0.0,0.0]), array([0,0,1.0]), R=R_av, I=N_val*I_val)
 
        x_current=x_min 
        y_current=y_min
        z_current=z_min

        point_num=0

        field_array=np.zeros((coords_total,6))
 
        while x_current <= x_max:

                y_current = y_min

                while y_current <= y_max:

                        z_current = z_min
        
                        while z_current <= z_max: 

                           # print(point_num)

                                smidge =array([x_current,y_current,z_current])
                                Bnet=c1.B(centre.r0+smidge)#+c2.B(c3.r0+smidge)
                                Bx = Bnet[0,0] 
                                By = Bnet[0,1]
                                Bz = Bnet[0,2]
                        
                                #B_net_mag = (sqrt(((Bx)**2) + ((By)**2) + ((Bz)**2)))

                                #Store values to an array 
                        
                                field_array[point_num,0] = x_current
                                field_array[point_num,1] = y_current
                                field_array[point_num,2] = z_current
                                field_array[point_num,3] = Bx
                                field_array[point_num,4] = By
                                field_array[point_num,5] = Bz
                                #field_array[point_num,6] = B_net_mag]                   

                                point_num=point_num+1

                                z_current = z_current+dz

                        y_current=y_current+dz

                x_current = x_current + dz

        return(field_array)
 
#Calculate total field from all coils
    while count<= coil_num-1:

        print(count)
   
        field=Field_Calc(N[count],I[count],dr[count],r[count],x_centre[count],y_centre[count],z_centre[count],x_normal[count],y_normal[count],z_normal[count])
        
        #Update total field array

        #Coordinates

        total_field[:,0] = field[:,0]
        total_field[:,1] = field[:,1]
        total_field[:,2] = field[:,2]

        #Magnetic field 
        total_field[:,3] = total_field[:,3]+field[:,3]
        total_field[:,4] = total_field[:,4]+field[:,4]
        total_field[:,5] = total_field[:,5]+field[:,5]


        count=count+1

    total_field[:,6] = sqrt(((total_field[:,3])**2) +((total_field[:,4])**2) +((total_field[:,5])**2)) 

    count = 0 

#Write csv file with data for paraview

    print("x,y,z,Bx,By,Bz,Bmag",file=B_file)

    while count <= coords_total-1: 

        print(total_field[count,0],",",total_field[count,1],",",total_field[count,2],",",total_field[count,3],",",total_field[count,4],",",total_field[count,5],",",total_field[count,6] ,file=B_file)
        count=count+1

    print ("Magnetic field calculated")


parser = argparse.ArgumentParser()
parser.add_argument('pf_coil_csv')
parser.add_argument('bounding_box')
parser.add_argument('config')
args = parser.parse_args()

pf_coil_path = args.pf_coil_csv
bb_filepath = args.bounding_box
json_path = args.config


with open(json_path, 'r') as file:
    data = json.load(file)

# Now, assign the values to variables
mesh_data = data['mesh_res']  # Assuming your data is under the 'geometry' key
dx = mesh_data['dx']
dy = mesh_data['dy']
dz = mesh_data['dz']


loop_field('Torus', pf_coil_path, bb_filepath, dx, dy, dz)

