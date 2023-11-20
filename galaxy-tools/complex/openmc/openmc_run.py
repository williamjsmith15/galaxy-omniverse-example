"""
A very simple script to run an OpenMC simulation with a tokamak source and a reflective boundary
    condition (0 and 90 degrees).

The script takes in a geometry file, a settings file and an output file path as arguments.

It is intentionally kept simple as the intention is to use this as an example of integrating
    scientific codes into Galaxy workflows  rather than a proper scientific application.
"""

import math
import json
import argparse

import openmc
import neutronics_material_maker as nmm
import openmc_plasma_source as ops

parser = argparse.ArgumentParser(
    prog="openmc_run.py",
    description="OpenMC example run script. Useage: python openmc_run.py <geometry> <settings>",
)

parser.add_argument(
    "geometry_file",
    help="Geometry CAD file for simulation. Format: h5m"
)
parser.add_argument(
    "config_file",
    help="Settings file with the run settings for the neutronics simulation. Format: JSON",
)

args = parser.parse_args()

geometry_file = args.geometry_file
config_file = args.config_file

# Read in settings file and split to individual sections
with open(config_file, 'r') as read_file:
    config = json.load(read_file)

geometry_config = config["geometry"]
settings_config = config["settings"]
plasma_config = config["plasma_params"]

# Set up the openmc model to add all the simulation settings to
model = openmc.model.Model()

##################
# MATERIALS
##################

# NOTE: Currently defining these statically
# Could be easily done dynamically in future with the JSON configuration file
blanket = nmm.Material.from_library(
    name="Lithium",
    enrichment=7.5,
    enrichment_target="Li6",
    enrichment_type="ao",
).openmc_material
blanket.name = "blanket"

firstwall = nmm.Material.from_library(name="Tungsten").openmc_material
firstwall.name = "firstwall"

divertor = nmm.Material.from_library(name="Tungsten").openmc_material
divertor.name = "divertor"

plasma = nmm.Material.from_library(name="DT_plasma").openmc_material
plasma.name = "plasma"

materials = openmc.Materials([blanket, firstwall, divertor, plasma])
model.materials = materials

##################
# GEOMETRY
##################

# NOTE: Currently defining most of this statically
# Could be easily done dynamically in future with the JSON configuration file

dagmc_univ = openmc.DAGMCUniverse(filename=geometry_file)

# creates an edge of universe boundary surface
vac_surf = openmc.Sphere(
    r=geometry_config["outer_sphere"], surface_id=9999, boundary_type="vacuum"
)

# creates reflective surfaces at 0 and 90 degrees
reflective_1 = openmc.Plane(
    a=math.sin(math.radians(0)),
    b=-math.cos(math.radians(0)),
    c=0.0,
    d=0.0,
    surface_id=9991,
    boundary_type="reflective",
)
reflective_2 = openmc.Plane(
    a=math.sin(math.radians(90)),
    b=-math.cos(math.radians(90)),
    c=0.0,
    d=0.0,
    surface_id=9990,
    boundary_type="reflective",
)
# specifies the region as below the universe boundary and inside the reflective surfaces
region = -vac_surf & -reflective_1 & +reflective_2


# creates a cell from the region and fills the cell with the dagmc geometry
containing_cell = openmc.Cell(cell_id=9999, region=region, fill=dagmc_univ)
geometry = openmc.Geometry(root=[containing_cell])

model.geometry = geometry


##################
# RUN SETTINGS
##################

settings = openmc.Settings()

# NOTE: Currently assuming a tokamak source
# Could be easily changed dynamically in future with the JSON configuration file
source_single = ops.TokamakSource(
    # Geometry parameters
    major_radius=geometry_config["major_radius"],
    minor_radius=geometry_config["minor_radius"],
    elongation=geometry_config["elongation"],
    triangularity=geometry_config["triangularity"],
    angles=(math.radians(0), math.radians(90)),
    pedestal_radius=0.8 * geometry_config["minor_radius"],
    # Plasma parameters
    mode=plasma_config["plasma_mode"],  # Confinement mode
    ion_density_centre=plasma_config["ion_density_centre"],
    ion_density_peaking_factor=plasma_config["ion_density_peaking_factor"],
    ion_density_pedestal=plasma_config["ion_density_pedestal"],
    ion_density_separatrix=plasma_config["ion_density_separatrix"],
    ion_temperature_centre=plasma_config["ion_temperature_centre"],
    ion_temperature_peaking_factor=plasma_config["ion_temperature_peaking_factor"],
    ion_temperature_pedestal=plasma_config["ion_temperature_pedestal"],
    ion_temperature_separatrix=plasma_config["ion_temperature_separatrix"],
    shafranov_factor=plasma_config["shafranov_factor"],
    ion_temperature_beta=plasma_config["ion_temperature_beta"],
)

settings.source = source_single.sources


##################
# SOURCE
##################

settings.batches = settings_config["batches"]
settings.particles = settings_config["particles"]
settings.run_mode = settings_config["run_mode"]

model.settings = settings

##################
# TALLIES
##################

tbr_tally = openmc.Tally(name="TBR")
tbr_tally.scores = ["H3-production"]

model.tallies = openmc.Tallies([tbr_tally])

##################
# RUN OPENMC
##################

model.export_to_xml()

openmc.run(tracks=True)
