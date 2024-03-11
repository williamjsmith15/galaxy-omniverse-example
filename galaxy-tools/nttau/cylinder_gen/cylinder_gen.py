import argparse
import json
import cadquery as cq
import numpy as np
from scipy.optimize import minimize


radial_build = [0.5, 0.1, 0.2, 0.8, 0.2, 0.5, 0.2, 0.5]
thickness = 0
height = 92.0

print("Height: ",height)

class REBCOCoilDesign:
    mu_0 = 4 * np.pi * 10**-7  # vacuum permeability
    B_target = 9  # T, target magnetic field

    def __init__(
        self,
        workplane="XY",
        YBCO_rho=6200,
        critical_current_density=1e10,
        max_supply_current=16.786e4,
        YBCO_cost=100,
        cu_cost=10.3,
        ss_cost=5,
        YBCO_cs=0.00009,
        coolant_cs=0.000009,
        cu_cs=0.000031,
        ss_cs=0.000108,
        min_i_rad=4.93,
        r_center=1.2,
        dr = 0.1, 
        dz= 0.1,
        z_center=0,
        max_supply_current_2=16.786e6,
    ):
        self.workplane = workplane
        self.YBCO_rho = YBCO_rho
        self.critical_current_density = critical_current_density
        self.max_supply_current = max_supply_current
        self.YBCO_cost = YBCO_cost
        self.cu_cost = cu_cost
        self.ss_cost = ss_cost
        self.YBCO_cs = YBCO_cs
        self.coolant_cs = coolant_cs
        self.cu_cs = cu_cs
        self.ss_cs = ss_cs
        self.total_cs = YBCO_cs + coolant_cs + cu_cs + ss_cs
        self.min_i_rad = min_i_rad
        self.turn_thickness = np.sqrt(self.total_cs)
        self.r_center = r_center
        self.z_center = z_center
        self.dr = dr 
        self.dz= dz
        self.max_supply_current = max_supply_current_2
        self.max_allowable_current = min(
            self.max_supply_current, self.critical_current_density / 3 * self.YBCO_cs
        )

        self.coil = self.make_coil()

    def num_turns(self, params):
        current, R_avg = params
        return 2 * R_avg * self.B_target / (self.mu_0 * current)

    def wire_length(self, params):
        current, R_avg = params
        N = self.num_turns(params)
        return 2 * np.pi * R_avg * N

    def current_constraint(self, params):
        current, R_avg = params
        return current - self.max_allowable_current

    def turns_constraint(self, params):
        current, R_avg = params
        N = self.num_turns(params)
        return N - np.round(N)

    def inner_radius_constraint(self, params):
        current, R_avg = params
        N = self.num_turns(params)
        i_rad = R_avg - 0.5 * N * self.turn_thickness
        return i_rad - self.min_i_rad

    def compute(self):
        bnds = ((1, None), (self.min_i_rad, None))
        initial_guess = [self.max_allowable_current, self.min_i_rad]

        cons = (
            {"type": "eq", "fun": self.current_constraint},
            {"type": "eq", "fun": self.turns_constraint},
            {"type": "ineq", "fun": self.inner_radius_constraint},
        )

        self.result = minimize(
            self.wire_length, initial_guess, bounds=bnds, constraints=cons
        )

    def make_coil(self):
        self.compute()
      #  N = self.num_turns(self.result.x)
        r_center=self.r_center 
        z_center=self.z_center 
        dr=self.dr 
        dz=self.dz
        i_rad = r_center - (0.5 * dr)
        o_rad = r_center + (0.5 * dr)
        z_max=z_center + (0.5 * dz)
        height = dz

        print("COIL VALS") 
        print(r_center,z_center,height,z_max)
        print(self.workplane)

        outer_coil = cq.Workplane(self.workplane).circle(o_rad).extrude(height)
        inner_coil = cq.Workplane(self.workplane).circle(i_rad).extrude(height)
        outer_coil=outer_coil.translate((0,z_max,0))
        inner_coil=inner_coil.translate((0,z_max,0))
        radii = [i_rad, o_rad]
        coil = outer_coil.cut(inner_coil)
        # display(coil)
        return coil,radii
        # display(coil)
        
    def calculate_cost(self):
        final_YBCO_cost = (
            self.wire_length(self.result.x)
            * self.YBCO_cs
            / self.total_cs
            * self.YBCO_cost
            * 1e-6
        )
        final_cu_cost = self.result.fun * self.cu_cs * self.cu_cost * 7900 * 1e-6
        final_ss_cost = self.result.fun * self.ss_cs * self.ss_cost * 7900 * 1e-6
        tot_mat_cost = final_YBCO_cost + final_cu_cost + final_ss_cost
        self.total_cost = round(tot_mat_cost * 9, 3)

    def print_results(self):
        self.compute()
        N = self.num_turns(self.result.x)
        i_rad = self.result.x[1] - 0.5 * np.sqrt(N) * self.turn_thickness
        o_rad = self.result.x[1] + 0.5 * np.sqrt(N) * self.turn_thickness
        height = np.sqrt(N) * self.turn_thickness
        current_density = self.result.x[0] / self.YBCO_cs

        print(
            "\n--------------------------------RESULTS--------------------------------\n"
        )

        """
        PARAMETERS
        """
        print("Field at center:", self.B_target, "T \n")
        print("Current:", round(self.result.x[0], 3), "A")
        print("Current Density:", round(current_density, 3), "A/m^2")
        print("Inner radius:", round(i_rad, 3), "m")
        print("Outer radius:", round(o_rad, 3), "m")
        print("Height:", round(height, 3), "m")
        print("Number of turns:", round(N))
        print("Length of wire:", round(self.wire_length(self.result.x), 2), "m\n")

        """
        COSTS
        """
        final_YBCO_cost = (
            self.wire_length(self.result.x)
            * self.YBCO_cs
            / self.total_cs
            * self.YBCO_cost
            * 1e-6
        )
        final_cu_cost = self.result.fun * self.cu_cs * self.cu_cost * 7900 * 1e-6
        final_ss_cost = self.result.fun * self.ss_cs * self.ss_cost * 7900 * 1e-6
        print("Cost of YBCO: $", round(final_YBCO_cost, 3), "M")
        print("Cost of copper: $", round(final_cu_cost, 3), "M")
        print("Cost of steel: $", round(final_ss_cost, 3), "M")

        tot_mat_cost = final_YBCO_cost + final_cu_cost + final_ss_cost
        print("Total material cost: $", round(tot_mat_cost, 3), "M")
        print("Cost to manufacture w/ mfr factor 9: $", round(tot_mat_cost * 9, 3), "M")
        self.total_cost = round(tot_mat_cost * 9, 3)

    def append_text_file(self, file_path):
        self.compute()
        R_avg = (i_rad + o_rad) / 2
        turns = round(N)
        current = round(self.result.x[0], 3)

        with open(file_path, "a") as file:
            file.write(f"{R_avg},{turns},{current},{self.r_center},{self.z_center}\n")

class Cylinder:
    def __init__(self,radial_build, height):
        reactor = cq.Assembly()
        outer_radius = 0
        layers = []
        i=0
        while i <=3:
            print(radial_build[i],type(radial_build[i]))
            outer_radius += round(float(radial_build[i]), 2)
            print("outer radius")
            print(outer_radius,round(float(radial_build[i]), 2),(radial_build[i]))
            if i == 0:
                cylinder = (
                    cq.Workplane("XY")
                    .cylinder(height, radial_build[i])
                )
                layers.append(cylinder)
            else:
                inner_radius = outer_prev
                cylinder = self.generate_hollow_cylinder(height, outer_radius, inner_radius)
                layers.append(cylinder)
            reactor.add(cylinder)
            self.reactor = reactor
            self.layers = layers
            outer_prev = outer_radius
            i=i+1
    def generate_hollow_cylinder(self,height, outer_radius, inner_radius):

        if outer_radius <= inner_radius:
            raise ValueError("outer_radius must be larger than inner_radius")

        
        cylinder1 = (
            cq.Workplane("XY")
            .cylinder(height, outer_radius)
        )
        cylinder2 = (
            cq.Workplane("XY")
            .cylinder(height, inner_radius)
        )

        cylinder=cylinder1.cut(cylinder2)
        print("radii: ",inner_radius,outer_radius)

        return cylinder

def make_coil(min_i_rad,current):
        coil_design = REBCOCoilDesign(min_i_rad=min_i_rad,workplane = "XY",max_supply_current=current)
        result = coil_design.result
        coil_design.calculate_cost()
        coil_cost = coil_design.total_cost
        coil, coil_radii = coil_design.make_coil()
    
        return coil, coil_radii, result, coil_cost

def generate_cylinder(radial_build, height, N_coils, inner_radius, current, output_filepath):
    total_cost = 0
    count = 0
    cylinder = Cylinder(radial_build, height)
    
    # for i,layer in enumerate(cylinder.layers):
    #     layer.val().exportStep(f"data/geometry_data/Cylindrical/layer{i}.step")

    coil_z = np.linspace(-height/2, height/2, N_coils)

    #Write coil info to csv file 

    
    coils = cq.Assembly()

    with open(output_filepath, "w") as file:
        file.write(f"N,I (A),Inner Radius,Outer radius,Coil_X,Coil_Y,Coil_Z,Normal X,Normal Y,Normal Z \n")  
   
        for coil_z in coil_z:
            coil, coil_radii, result, coil_cost = make_coil(inner_radius,current )
            outer_radius=inner_radius + (0.1* inner_radius) 
            coil = coil.translate(cq.Vector(0,0,coil_z))
            total_cost += coil_cost
            print("Total Cost of Coil",count,"is:", coil_cost)
            cylinder.reactor.add(coil)
            coils.add(coil)
            count+=1
            if count ==1: 
                I_val = 10*current 
            elif count ==1: 
                I_val = 10*current
            else: 
                I_val = current 

            file.write(f"1,{I_val},{inner_radius},{outer_radius},0,0,{coil_z},0,0,1\n")
        
        
        #print("Count : ",count,N_coils)
        cylinder.reactor.save("reactor.step")
        coils.save("coils.step")
        print("Total Cost of all Coils is:", total_cost)
        return cylinder




parser = argparse.ArgumentParser()
parser.add_argument('file_path')
parser.add_argument('output_filepath')
args = parser.parse_args()
file_path = args.file_path
output_csv = args.output_filepath
# Open the file and load the data
with open(file_path, 'r') as file:
    data = json.load(file)

# Now, assign the values to variables
geometry_data = data['geometry']  # Assuming your data is under the 'geometry' key
radial_build = geometry_data['radial_build']
reactor_height = geometry_data['height']
coil_num = geometry_data['number_of_coils']
current = geometry_data['current']


inner_radius = sum(radial_build)+3

generate_cylinder(radial_build, reactor_height, coil_num, inner_radius,current, output_csv)
    
