from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Hold a horizontal cable bundle against a wall with one M4 screw.

    bundle_diameter: measured width across the cable bundle
    """
    clearance = 0.6
    wall_thickness = 3.0
    floor_thickness = 2.4
    holder_length = 12.0
    front_wall_thickness = 3.0

    clear_width = bundle_diameter + clearance
    cable_radius = clear_width / 2.0
    cable_center_z = floor_thickness + cable_radius
    front_wall_height = cable_center_z + cable_radius

    screw_hole_radius = 2.2
    screw_center_z = cable_center_z + bundle_diameter + 3.2
    back_height = screw_center_z + 5.0
    holder_depth = wall_thickness + clear_width + front_wall_thickness

    back = Box(
        wall_thickness,
        holder_length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        holder_depth,
        holder_length,
        floor_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    front = Pos(wall_thickness + clear_width, 0, 0) * Box(
        front_wall_thickness,
        holder_length,
        front_wall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = back + floor + front

    screw_bore = (
        Cylinder(
            screw_hole_radius,
            wall_thickness + 0.2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        .rotate(Axis.Y, 90)
        .translate((-0.1, holder_length / 2.0, screw_center_z))
    )

    return body - screw_bore
