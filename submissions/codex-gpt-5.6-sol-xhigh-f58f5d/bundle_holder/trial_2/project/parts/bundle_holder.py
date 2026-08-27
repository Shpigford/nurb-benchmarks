from nurb import *


@part
def bundle_holder(bundle_diameter: float = 8.0):
    """A wall-mounted, open-top cradle for a horizontal cable bundle.

    bundle_diameter: measured width of the cable bundle the cradle holds
    """
    clearance = 0.4
    cable_space = bundle_diameter + clearance

    length = 14.0
    wall_thickness = 3.0
    retaining_thickness = 1.2
    floor_thickness = 1.2

    screw_hole_diameter = 4.4
    screw_head_diameter = 8.4
    screw_center_z = floor_thickness + cable_space + screw_head_diameter / 2 + 1.2
    plate_height = screw_center_z + screw_head_diameter / 2 + 0.8

    front_wall_x = wall_thickness + cable_space
    outer_depth = front_wall_x + retaining_thickness
    retaining_height = floor_thickness + cable_space

    plate = Box(
        wall_thickness,
        length,
        plate_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    floor = Box(
        outer_depth,
        length,
        floor_thickness,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    retaining_wall = Pos(front_wall_x, 0, 0) * Box(
        retaining_thickness,
        length,
        retaining_height,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    body = plate + floor + retaining_wall

    # The hole is centered through the 3 mm wall plate. Its front opening is the
    # pan-head seat, with unobstructed space in +X for the head and driver.
    screw_hole = Pos(wall_thickness / 2, 0, screw_center_z) * Cylinder(
        screw_hole_diameter / 2,
        wall_thickness + 2.0,
        rotation=(0, 90, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )

    return body - screw_hole
