from nurb import *


@part
def cable_clip(bundle_diameter: float = measured("bundle_diameter"), draft=False):
    """A screw-down, open-top clip for a cable bundle.

    bundle_diameter: measured diameter of the cable bundle held by the channel.
    """
    if bundle_diameter <= 0.0:
        reject("Bundle diameter must be greater than zero.", "bundle_diameter")

    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    channel_wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    mounting_tab_length = 10.0
    screw_hole_diameter = 4.2

    # The channel is made from a flat floor and two full-length walls so its
    # interior remains square and unmodified by the exterior polish policy.
    clip_width = channel_width + 2.0 * channel_wall_thickness
    base = Box(
        clip_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    left_wall = Box(
        channel_wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((0.0, 0.0, base_thickness))
    right_wall = Box(
        channel_wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate(
        (channel_wall_thickness + channel_width, 0.0, base_thickness)
    )
    mounting_tab = Box(
        mounting_tab_length,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((-mounting_tab_length, 0.0, 0.0))

    body = base + left_wall + right_wall + mounting_tab
    screw_hole = Cylinder(
        screw_hole_diameter / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((-mounting_tab_length / 2.0, part_length / 2.0, 0.0))

    return body - screw_hole
