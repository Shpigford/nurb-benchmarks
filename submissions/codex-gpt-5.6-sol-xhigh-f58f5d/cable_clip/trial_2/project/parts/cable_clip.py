from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter")):
    """A screw-down clip for a cable bundle running along Y.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    channel_clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_width = 4.2

    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2.0 * wall_thickness

    base = Box(
        body_width,
        part_length,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    left_wall = Pos(-body_width / 2.0, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    right_wall = Pos(channel_width / 2.0, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    tab = Pos(body_width / 2.0, 0, 0) * Box(
        tab_length,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    screw_hole = Pos(body_width / 2.0 + tab_length / 2.0, 0, 0) * Cylinder(
        screw_hole_width / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return (base + left_wall + right_wall + tab) - screw_hole
