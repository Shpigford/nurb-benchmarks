from math import sqrt

from nurb import *


def _cylinder_along_x(radius, end_x, length, y, z):
    """A cylinder whose axis points out from the wall."""
    return Cylinder(
        radius,
        length,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).rotate(Axis.Y, -90).translate((end_x, y, z))


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """A low-material wall clip for one horizontal cable bundle.

    bundle_diameter: measured outside diameter of the cable bundle.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    # The open channel is deliberately wider than the measured bundle by 0.8 mm:
    # 0.4 mm of fit clearance plus 0.4 mm of breathing room around the bundle.
    wall_thickness = 3.6
    base_thickness = max(2.8, bundle_diameter * 0.35)
    part_length = 12.0
    channel_width = bundle_diameter + 0.8
    lip_thickness = 2.0

    cable_center_x = wall_thickness + channel_width / 2.0
    cable_center_z = base_thickness + (bundle_diameter + 0.4) / 2.0 + 0.2
    outward_move = 1.0
    blocking_reach = sqrt(
        ((bundle_diameter + 0.4) / 2.0) ** 2
        - (channel_width / 2.0 - outward_move) ** 2
    )
    lip_height = cable_center_z + blocking_reach + 0.4

    # Keep an 8.8 mm-diameter M4 pan-head/driver clearance volume above the bundle.
    head_radius = 4.4
    screw_y = part_length / 2.0
    screw_z = cable_center_z + (bundle_diameter + 0.4) / 2.0 + head_radius + 0.5
    back_height = screw_z + head_radius + 1.3

    front_x = wall_thickness + channel_width + lip_thickness
    back = Box(
        wall_thickness,
        part_length,
        back_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    floor = Box(
        front_x,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    retaining_lip = Pos(wall_thickness + channel_width, 0, 0) * Box(
        lip_thickness,
        part_length,
        lip_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    body = back + floor + retaining_lip

    # The shank enters through the wall-facing back.  Its seat is 2.6 mm inboard,
    # then the wider head/driver clearance opens uninterrupted toward +X.
    seat_x = 2.4
    shank_bore = _cylinder_along_x(2.2, seat_x, seat_x + 0.1, screw_y, screw_z)
    head_clearance = _cylinder_along_x(
        head_radius,
        wall_thickness + 0.2,
        wall_thickness - seat_x + 0.2,
        screw_y,
        screw_z,
    )
    return body - shank_bore - head_clearance
