from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
    """Screw-down cable clip with a square, open-top channel.

    bundle_diameter: diameter of the cable bundle held by the channel
    """
    channel_width = bundle_diameter + 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    channel_depth = bundle_diameter
    length = 12.0
    tab_length = 10.0
    hole_diameter = 4.2

    channel_outer_width = channel_width + 2.0 * wall_thickness
    overall_width = channel_outer_width + tab_length

    base = Box(
        channel_outer_width,
        length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    left_wall = Pos(0, 0, base_thickness) * Box(
        wall_thickness,
        length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    right_wall = Pos(channel_outer_width - wall_thickness, 0, base_thickness) * Box(
        wall_thickness,
        length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    tab = Pos(channel_outer_width, 0, 0) * Box(
        tab_length,
        length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = base + left_wall + right_wall + tab
    screw_hole = Pos(overall_width - tab_length / 2.0, length / 2.0, 0) * Cylinder(
        hole_diameter / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body - screw_hole
