from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
    """A screw-down, open-top clip for a cable bundle.

    bundle_diameter: measured diameter of the cable bundle held by the channel
    """
    channel_clearance = 0.4
    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    outer_width = channel_width + 2 * wall_thickness

    base = Box(outer_width, part_length, base_thickness, align=(Align.MIN, Align.MIN, Align.MIN))
    left_wall = Box(wall_thickness, part_length, channel_depth, align=(Align.MIN, Align.MIN, Align.MIN)).translate((0, 0, base_thickness))
    right_wall = Box(wall_thickness, part_length, channel_depth, align=(Align.MIN, Align.MIN, Align.MIN)).translate(
        (wall_thickness + channel_width, 0, base_thickness)
    )
    tab = Box(tab_length, part_length, base_thickness, align=(Align.MIN, Align.MIN, Align.MIN)).translate((outer_width, 0, 0))
    screw_hole = Cylinder(screw_hole_diameter / 2, base_thickness, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate(
        (outer_width + tab_length / 2, part_length / 2, 0)
    )

    return (base + left_wall + right_wall + tab) - screw_hole
