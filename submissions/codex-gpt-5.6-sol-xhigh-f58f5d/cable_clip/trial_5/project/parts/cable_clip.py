from build123d import Align, Box, Cylinder, Pos
from nurb import part


@part
def cable_clip(bundle_diameter: float = 8.0):
    """Screw-down clip for a cable bundle running along the Y axis.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    channel_outer_width = channel_width + 2.0 * wall_thickness
    overall_height = base_thickness + channel_depth

    minimum = (Align.MIN, Align.MIN, Align.MIN)

    base = Box(
        channel_outer_width,
        part_length,
        base_thickness,
        align=minimum,
    )
    left_wall = Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=minimum,
    )
    left_wall = Pos(0.0, 0.0, base_thickness) * left_wall

    right_wall = Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=minimum,
    )
    right_wall = Pos(
        wall_thickness + channel_width,
        0.0,
        base_thickness,
    ) * right_wall

    mounting_tab = Box(
        tab_length,
        part_length,
        base_thickness,
        align=minimum,
    )
    mounting_tab = Pos(channel_outer_width, 0.0, 0.0) * mounting_tab

    screw_hole = Cylinder(
        screw_hole_diameter / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    screw_hole = Pos(
        channel_outer_width + tab_length / 2.0,
        part_length / 2.0,
        0.0,
    ) * screw_hole

    clip = base + left_wall + right_wall + mounting_tab
    clip = clip - screw_hole

    # Keep the channel floor and walls deliberately square and unpolished: their
    # exact dimensions are the cable's functional mating geometry.
    assert overall_height == base_thickness + bundle_diameter
    return clip
