import cadquery as cq
import numpy as np
from numpy import linspace
from pylab import *
import csv
import os

# from coil_functions import create_coil
import csv

# Create a sample assembly


def TF_step(r, filepath, z_thickness, r_thickness, tf_coil_path):
    assy = cq.Assembly()

    coil_count = 1

    # 12 coils
    TF_num = 12

    coil_num = 12
    angle_tot = 2 * pi

    # angle to rotate by
    angle_int = angle_tot / coil_num

    # print(angle_tot,angle_int)

    rev_1 = open(filepath, "r")

    file = csv.DictReader(rev_1)

    xorig_str = []
    yorig_str = []

    count = 0

    for col in file:
        # Read in values from vessel file
        xorig_str.append(col["X"])
        yorig_str.append(col["Y"])
        count = count + 1

    # Create correct size arrays to store info about each coil
    tot_point = count
    # print("tot_point = ", tot_point)

    xorig = np.zeros(tot_point + 1)
    yorig = np.zeros(tot_point + 1)
    zorig = np.zeros(tot_point + 1)

    xouter = np.zeros(tot_point + 1)
    youter = np.zeros(tot_point + 1)
    zouter = np.zeros(tot_point + 1)

    xinner = np.zeros(tot_point + 1)
    yinner = np.zeros(tot_point + 1)
    zinner = np.zeros(tot_point + 1)

    orig_tot = np.zeros((tot_point + 1, 3))
    orig_out = np.zeros((tot_point + 1, 3))

    x1 = np.zeros(tot_point + 1)
    y1 = np.zeros(tot_point + 1)
    z1 = np.zeros(tot_point + 1)

    x2 = np.zeros(tot_point + 1)
    y2 = np.zeros(tot_point + 1)
    z2 = np.zeros(tot_point + 1)

    x3 = np.zeros(tot_point + 1)
    y3 = np.zeros(tot_point + 1)
    z3 = np.zeros(tot_point + 1)

    x4 = np.zeros(tot_point + 1)
    y4 = np.zeros(tot_point + 1)
    z4 = np.zeros(tot_point + 1)

    points_array = np.zeros((tot_point + 1, 3))
    points2_array = np.zeros((tot_point + 1, 3))
    points3_array = np.zeros((tot_point + 1, 3))
    points4_array = np.zeros((tot_point + 1, 3))

    count = 0
    # convert to correct type (integer/float) and create complete loop

    while count <= tot_point:
        if count <= tot_point - 1:
            xorig[count] = float(xorig_str[count])
            yorig[count] = float(yorig_str[count])
            # print(count)

        else:
            xorig[count] = xorig[0]
            yorig[count] = yorig[0]
        # print(count)

        # print(xorig[count],yorig[count])

        count = count + 1

    # print(xorig[tot_point],yorig[tot_point],xorig[0],yorig[0])
    coil_count = 1

    # Centre system around 0,0,0
    # already centred so no change

    xorig = xorig  # - x_centre
    yorig = yorig  # - y_centre

    # Centre loop around 0,0,0 and scale
    xloop_c = (max(xorig) + min(xorig)) / 2
    yloop_c = (max(yorig) + min(yorig)) / 2

    # print("Loop centre: ", xloop_c,yloop_c)

    # Create coordinates of loop centred around 0,0,0
    xnew = xorig - xloop_c
    ynew = yorig - yloop_c

    # print (xnew)
    # print (ynew)
    z_extend = z_thickness
    dr = r_thickness
    r_change = dr - r

    r_dr_ratio = dr / r

    # Scale coordinates of loop centred around 0,0,0 and shift
    # Creates loop with the whole system centred at 0,0,0

    # outer represents outer edge of the TF coil
    # inner represents the inner edge of the TF coil ( near vessel)

    xouter = (xnew * (1 + (r_dr_ratio))) + xloop_c
    xinner = (xnew * (1)) + xloop_c
    youter = (ynew * (1 + (r_dr_ratio))) + yloop_c
    yinner = (ynew * (1)) + yloop_c
    zouter = zorig + (z_extend / 2)
    zinner = zorig - (z_extend / 2)

    # Centre coords used for defining the loop for magnet code
    xcentre = (xnew * (1 + ((r_dr_ratio)) / 2)) + xloop_c
    ycentre = (ynew * (1 + ((r_dr_ratio)) / 2)) + yloop_c
    zcentre = zorig

    orig_tot[:, 0] = xinner
    orig_tot[:, 1] = yinner
    orig_tot[:, 2] = zinner

    orig_out[:, 0] = xouter
    orig_out[:, 1] = youter
    orig_out[:, 2] = zinner

    # print(xloop_c, yloop_c)
    # print(xouter)
    # print(youter)
    # Scaled loop created for thickness of coil

    count = 0
    outer_file = open("outer.csv", "w")
    inner_file = open("inner.csv", "w")
    #  print("printing test values")
    print("x,y,z", file=outer_file)
    print("x,y,z", file=inner_file)

    # Open a single file for writing all the coil data
    with open(tf_coil_path, "w") as TF_file:
        coil_count = 1

        while coil_count <= coil_num:
            # Write a header for each coil
            print(f"TF Coil {coil_count}", file=TF_file)
            print("x,y,z", file=TF_file)

            angle = angle_int * coil_count

            # new_coords
            x1 = (xcentre * cos(angle)) + (zcentre * sin(angle))  # + x_centre
            z1 = ((-xcentre) * sin(angle)) + (zcentre * cos(angle))
            y1 = ycentre  # + y_centre

            count = 0
            while count <= tot_point:
                print(f"{x1[count]},{y1[count]},{z1[count]}", file=TF_file)
                count += 1

            coil_count += 1
            # No need to close the file, 'with' statement handles that


        #  print(x1)

        points = points_array.tolist()
        points2 = points2_array.tolist()
        points3 = points3_array.tolist()
        points4 = points4_array.tolist()

        points_tot = orig_tot[:].tolist()
        points_out = orig_out[:].tolist()
    # print("total points")
    # print(points_tot)

    # Extrude by 0.35 in z direction to make 3D
    # Creates completely filled in shape
    p6 = cq.Workplane("front").polyline(points_out).close().extrude(z_thickness)

    # Extrude inner surface in z
    p5 = cq.Workplane("front").polyline(points_tot).close().extrude(z_thickness)

    # Remove filled in inner surface from outer to create the correct coil shape
    p7 = p6.cut(p5)

    i = 1

    # Rotate coils around by set angle to generate all 12 coils
    print("ADDING TF COILS")
    while i <= TF_num:
        ob = "TF_" + str(i)
        angle = (360.0 / TF_num) * i
        print(i, angle)

        # (0,0,0) is the centre point, (0,1,0) is the axis of rotation
        p8 = p7.rotate((0, 0, 0), (0, 1, 0), angle)
        # move coil by necessary coords
        p8 = p8.translate((0, 0, 0))
        # Add coil to the step file
        assy.add(p8, color=cq.Color(1, 1, 1), name=ob)
        i = i + 1

    return assy
