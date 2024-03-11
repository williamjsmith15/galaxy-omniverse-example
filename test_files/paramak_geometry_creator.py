"""
This is a file to create an example geometry for the OpenMC workflow tool
The geometry is a simple reactor setup with a plasma, blanket, first wall and divertor

This can be run in the docker container williamjsmith15/omniverse-openmc:05062023 with the command:
    docker run -it -v $PWD/:/home/ williamjsmith15/omniverse-openmc:05062023 /bin/bash
which will mount the current directory to the docker container.

RUn the script with:
    python paramak_geometry_creator.py <openmc_config.json>

where the json file is the one created in the openmc_json_creator.py file
"""
import json
import argparse
import numpy as np

import paramak
from stl_to_h5m import stl_to_h5m


parser = argparse.ArgumentParser(
    prog="paramak_generator.py", description="Paramak geometry generator"
)

parser.add_argument(
    "config_file",
    help="Config .json file with the parameters for the geometry creation. Format: JSON.",
)
args = parser.parse_args()
config_path = args.config_file


def parametric_blanket(config_dict):
    """
    Generates a parametric blanket geometry for the OpenMC workflow tool

    Inputs:
        config_dict (dict): Dictionary of the parameters for the geometry creation
    Outputs:
        None
    """
    plasma = paramak.Plasma(
        minor_radius=config_dict["minor_radius"],
        major_radius=config_dict["major_radius"],
        triangularity=config_dict["triangularity"],
        elongation=config_dict["elongation"],
        rotation_angle=90,
    )

    firstwall = paramak.BlanketFP(
        plasma=plasma,
        thickness=config_dict["first_wall_thickness"],
        stop_angle=230,
        start_angle=-60,
        offset_from_plasma=config_dict["plasma_offset"],
        rotation_angle=90,
        num_points=100,
        color=list(
            np.random.rand(3,)
        ),
    )

    blanket_cut = paramak.BlanketFP(
        plasma=plasma,
        thickness=config_dict["blanket_thickness"]
        + config_dict["first_wall_thickness"]
        + 5,
        stop_angle=230,
        start_angle=-60,
        offset_from_plasma=config_dict["plasma_offset"]
        - config_dict["first_wall_thickness"],
        rotation_angle=90,
    )

    blanket = paramak.BlanketFP(
        plasma=plasma,
        thickness=config_dict["blanket_thickness"],
        stop_angle=230,
        start_angle=-60,
        offset_from_plasma=config_dict["plasma_offset"]
        + config_dict["first_wall_thickness"],
        rotation_angle=90,
    )

    divertor = paramak.BlanketFP(
        plasma=plasma,
        thickness=config_dict["blanket_thickness"],
        stop_angle=270,
        start_angle=-90,
        offset_from_plasma=config_dict["plasma_offset"]
        + config_dict["first_wall_thickness"],
        rotation_angle=90,
        cut=blanket_cut,
        color=list(
            np.random.rand(3,)
        ),
    )

    divertor.export_stl("divertor.stl")
    blanket.export_stl("blanket.stl")
    firstwall.export_stl("firstwall.stl")
    plasma.export_stl("plasma.stl")
    # reactor = paramak.Reactor([divertor, blanket, firstwall, plasma])

    stl_to_h5m(
        files_with_tags=[
            ("divertor.stl", "divertor"),
            ("blanket.stl", "blanket"),
            ("firstwall.stl", "firstwall"),
            ("plasma.stl", "plasma"),
        ],
        h5m_filename="dagmc.h5m",
    )


if __name__ == "__main__":
    with open(config_path, "r") as f:
        data = json.load(f)
        config = data["geometry"]

    parametric_blanket(config)
