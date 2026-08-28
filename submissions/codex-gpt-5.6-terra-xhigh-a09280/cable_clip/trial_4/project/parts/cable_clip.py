from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """A screw-down, open-top clip for a cable bundle.

    bundle_diameter: measured diameter of the cable bundle held in the channel.
    """
    channel_clearance = 0.4
    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    clip_width = channel_width + 2.0 * wall_thickness
    total_width = tab_length + clip_width

    # The base is the mounting tab and the 3 mm floor beneath the channel.
    base = Box(
        total_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    left_wall = Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((tab_length, 0.0, base_thickness))
    right_wall = Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((tab_length + wall_thickness + channel_width, 0.0, base_thickness))

    body = base + left_wall + right_wall
    screw_hole = Cylinder(
        screw_hole_diameter / 2.0,
        base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((tab_length / 2.0, part_length / 2.0, -1.0))

    # Keep the fit-critical channel perfectly square and leave the bed face flat.
    return body - screw_hole
