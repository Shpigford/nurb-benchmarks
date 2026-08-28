from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """A low-profile, wall-mounted cable-bundle clip.

    bundle_diameter: measured diameter of the cable bundle held by the clip.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    # The bundle has 0.2 mm radial clearance, making an 8.0 mm bundle fit in
    # an 8.4 mm circular envelope. The open top lets a bundle be threaded
    # through the clip while the floor and short front rail retain it in use.
    fit_diameter = bundle_diameter + 0.4
    fit_radius = fit_diameter / 2.0

    holder_length = 14.0
    back_thickness = 3.8
    floor_thickness = 2.6
    rail_thickness = 2.2
    # End the rail 1 mm below the bundle center. That leaves a generous round
    # clearance envelope while still catching a 1 mm outward displacement.
    rail_height = max(2.0, fit_radius - 1.0)

    cable_center_x = back_thickness + fit_radius
    cable_center_z = floor_thickness + fit_radius
    front_inner_x = back_thickness + fit_diameter

    # Keep the M4 head and driver above the cable's clearance envelope. The
    # 4.4 mm shaft has 2.6 mm of material before its 8.6 mm head recess, so
    # an 8.4 mm pan head and driver clear the whole front-side approach.
    screw_y = holder_length / 2.0
    screw_z = cable_center_z + fit_radius + 4.6
    back_height = screw_z + 6.5
    head_recess_depth = 1.2

    back = Box(
        back_thickness,
        holder_length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        front_inner_x + rail_thickness - back_thickness,
        holder_length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((back_thickness, 0.0, 0.0))
    retaining_rail = Box(
        rail_thickness,
        holder_length,
        rail_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((front_inner_x, 0.0, floor_thickness))

    body = back + floor + retaining_rail

    shaft_bore = Cylinder(
        2.2,
        back_thickness + 0.4,
        rotation=(0.0, 90.0, 0.0),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((-0.2, screw_y, screw_z))
    head_clearance = Cylinder(
        4.3,
        head_recess_depth + 0.4,
        rotation=(0.0, 90.0, 0.0),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((back_thickness - head_recess_depth, screw_y, screw_z))

    return body - shaft_bore - head_clearance
