import cadquery as cq
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('file_path')
args = parser.parse_args()
file_path = args.file_path

# Open the file and load the data
with open(file_path, 'r') as file:
    data = json.load(file)

def reactor_building(radial_build, major_rad, scale_factor, shield_thickness, contain_thickness):
    reactor_core_radius = sum(radial_build) + 0.8 + major_rad
    reactor_core_height = 2 * reactor_core_radius

    def create_roof(roof_type, reactor_building_radius, building_height):
        roof_thickness = 0.3  # Adjust as needed
        offset_height = building_height / 2 + roof_thickness / 2

        if roof_type == "flat":
            return (
                cq.Workplane("ZX")
                .transformed(offset=(0, 0, offset_height))
                .cylinder(roof_thickness, reactor_building_radius)
            )
        elif roof_type == "domed":
            outer_radius = reactor_building_radius
            inner_radius = outer_radius - contain_thickness

            outer_sphere = (
                cq.Workplane("ZX").transformed(offset=(0, 0, 0)).sphere(outer_radius)
            )

            inner_sphere = (
                cq.Workplane("ZX").transformed(offset=(0, 0, 0)).sphere(inner_radius)
            )

            hemisphere = outer_sphere.cut(inner_sphere)
            hemisphere = hemisphere.translate((0, offset_height, 0))
            cut_box = (
                cq.Workplane("ZX")
                .box(3 * outer_radius, 3 * outer_radius, 2 * outer_radius)
                .translate((0, 0, 0))
            )
            hemisphere = hemisphere.cut(cut_box)
            return hemisphere
        elif roof_type == "cone":
            cone_height = roof_thickness * 4  # Define the height of the cone roof
            bottom_radius = reactor_building_radius
            wall_thickness = 0.2
            # Create a cylinder
            cone_base = cq.Workplane("ZX").cylinder(cone_height, bottom_radius)
            # Apply a chamfer to the top edge to create the cone shape
            truncated_cone = cone_base.edges(">Y").chamfer(cone_height * 0.75)

            inner_radius = bottom_radius - wall_thickness
            inner_cone = cq.Workplane("ZX").cylinder(cone_height, inner_radius)

            # Apply a chamfer to the top edge of the inner cone to match the outer cone
            truncated_inner_cone = (
                inner_cone.edges(">Y")
                .chamfer(cone_height * 0.75)
                .translate((0, -0.3, 0))
            )

            # Cut the inner cone from the outer cone to create a hollow cone
            truncated_cone = truncated_cone.cut(truncated_inner_cone)

            # Translate the truncated cone to the correct position
            cone_translated = truncated_cone.translate((0, offset_height, 0))

            return cone_translated
        else:
            raise ValueError("Invalid roof type")

    def generate_hollow_cylinder(height, outer_radius, inner_radius, offset=(0, 0, 0)):
        if outer_radius <= inner_radius:
            raise ValueError("outer_radius must be larger than inner_radius")

        cylinder1 = (
            cq.Workplane("ZX").transformed(offset=offset).cylinder(height, outer_radius)
        )
        cylinder2 = (
            cq.Workplane("ZX").transformed(offset=offset).cylinder(height, inner_radius)
        )

        cylinder = cylinder1.cut(cylinder2)

        return cylinder

    reactor_shielding = generate_hollow_cylinder(
        reactor_core_height,
        reactor_core_radius,
        reactor_core_radius - shield_thickness,
    )

    BUILDING_SCALE_FACTOR = scale_factor
    reactor_building = generate_hollow_cylinder(
        reactor_core_height * BUILDING_SCALE_FACTOR,
        reactor_core_radius * BUILDING_SCALE_FACTOR,
        reactor_core_radius * BUILDING_SCALE_FACTOR - contain_thickness,
    )

    reactor_core_floor = (
        cq.Workplane("ZX")
        .transformed(offset=(0, 0, -reactor_core_height / 2))
        .cylinder(0.3, reactor_core_radius)
    )

    reactor_building_floor = (
        cq.Workplane("ZX")
        .transformed(offset=(0, 0, -reactor_core_height * BUILDING_SCALE_FACTOR / 2))
        .cylinder(0.3, reactor_core_radius * BUILDING_SCALE_FACTOR)
    )

    support_structure_upper = generate_hollow_cylinder(
        0.3,
        reactor_core_radius * BUILDING_SCALE_FACTOR,
        reactor_core_radius,
        (0, 0, reactor_core_height / 2),
    )

    support_structure_middle = generate_hollow_cylinder(
        0.3,
        reactor_core_radius * BUILDING_SCALE_FACTOR,
        reactor_core_radius,
        (0, 0, 0),
    )

    support_structure_lower = generate_hollow_cylinder(
        0.3,
        reactor_core_radius * BUILDING_SCALE_FACTOR,
        reactor_core_radius,
        (0, 0, -reactor_core_height / 2),
    )

    building_height = reactor_core_height * BUILDING_SCALE_FACTOR
    roof = create_roof(
        "cone", reactor_core_radius * BUILDING_SCALE_FACTOR, building_height
    )

    # total_structure = reactor_shielding.union(hemisphere)
    total_structure = reactor_shielding.union(reactor_building)
    total_structure = total_structure.union(reactor_core_floor)
    total_structure = total_structure.union(reactor_building_floor)
    total_structure = total_structure.union(support_structure_upper)
    total_structure = total_structure.union(support_structure_middle)
    total_structure = total_structure.union(support_structure_lower)
    total_structure = total_structure.union(roof)
    box1 = cq.Workplane("front").box(100, 100, 100).translate((0, 0, 50))
    total_structure = total_structure.cut(box1)

    return total_structure

geometry_data = data['geometry']  # Assuming your data is under the 'geometry' key
aspect_ratio = geometry_data['aspect_ratio']
radial_build = geometry_data['radial_build']

containment_data = data['containment_vessel']
building_sf = containment_data['building_scale_factor']
shield_thickness = containment_data['shield_thickness']
contain_thick = containment_data['containment_vessel_thickness']

major_radius = aspect_ratio * radial_build[0]


containment_vessel = reactor_building(radial_build, major_radius, building_sf, shield_thickness, contain_thick)
cq.exporters.export(containment_vessel, "containment.step")