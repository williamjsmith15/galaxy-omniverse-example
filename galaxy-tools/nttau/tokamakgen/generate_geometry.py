import TokamakGen as tg
import cadquery as cq
import csv
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('config_file_path')
parser.add_argument('TF_coil_path')
parser.add_argument('PF_coil_path')
args = parser.parse_args()
config = args.config_file_path
tf_coil_path = args.TF_coil_path
pf_coil_path = args.PF_coil_path
# Open the file and load the data
with open(config, 'r') as file:
    data = json.load(file)

# Now, assign the values to variables
geometry_data = data['geometry']  # Assuming your data is under the 'geometry' key
aspect_ratio = geometry_data['aspect_ratio']
radial_build = geometry_data['radial_build']
component_names = geometry_data['component_names']
TF_dz = geometry_data['TF_dz']
TF_dr = geometry_data['TF_dr']
PF_dr = geometry_data['PF_dr']
PF_dz = geometry_data['PF_dz']
With_Sol = geometry_data['With_Sol']

# output_filename = args.output_filename
print("Solenoid Flag: ", With_Sol)

# radial_build = [0.16, 0.04, 0.03, 0.03, 0.06]
# component_names = ["Plasma", "Vacuum", "First Wall", "Blanket", "Vessel"]
major_rad = aspect_ratio * radial_build[0]
max_a = sum(radial_build)
print(max)

# Init csv 
with open(pf_coil_path, "a", newline="") as csvfile:  # 'a' is for append mode
    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(
        [
                "R_turns",
                "Z_turns",
                "I",
                "r_av",
                "dr",
                "dz",
                "coil_x",
                "coil_y",
                "coil_z",
                "normal_x",
                "normal_y",
                "normal_z",
            ]
        )

reactor, coils, radial_build = tg.run_code(
    radial_build, component_names, aspect_ratio, TF_dz, TF_dr, PF_dz, PF_dr, With_Sol, tf_coil_path, pf_coil_path
)
reactor.save("reactor.step")
coils.save("coils.step")
radial_build.save("radial_build.step")