from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down clip for a cable bundle running along Y.

    bundle_diameter: diameter of the cable bundle held by the channel
    """
    channel_clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    mounting_hole_diameter = 4.2

    channel_width = bundle_diameter + channel_clearance
    channel_outer_width = channel_width + 2.0 * wall_thickness

    base = Box(
        channel_outer_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    tab = Pos(-tab_length, 0, 0) * Box(
        tab_length,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    left_wall = Pos(0, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        bundle_diameter,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    right_wall = Pos(wall_thickness + channel_width, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        bundle_diameter,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = base + tab + left_wall + right_wall

    mounting_hole = Pos(-tab_length / 2.0, part_length / 2.0, 0) * Cylinder(
        mounting_hole_diameter / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - mounting_hole

    # Keep the channel floor and inner walls square and dimensionally exact.
    return body
