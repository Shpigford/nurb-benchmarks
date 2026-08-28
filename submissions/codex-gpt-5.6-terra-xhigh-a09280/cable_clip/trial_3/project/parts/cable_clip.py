from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
    """Screw-down, open-top cable-bundle clip.

    bundle_diameter: measured cable-bundle diameter; it sets the channel depth
        and, with 0.4 mm clearance, the channel width.
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    clip_width = wall_thickness + channel_width + wall_thickness
    clip_height = base_thickness + channel_depth

    # The channel is intentionally an unpolished rectangular subtraction: its
    # floor and vertical walls remain square and dimensionally exact.
    clip = Box(clip_width, part_length, clip_height).translate((0, 0, clip_height / 2)).cut(
        Box(channel_width, part_length, channel_depth).translate(
            (0, 0, base_thickness + channel_depth / 2)
        )
    )

    tab = Box(tab_length, part_length, base_thickness).translate(
        (clip_width / 2 + tab_length / 2, 0, base_thickness / 2)
    )
    screw_hole = Cylinder(screw_hole_diameter / 2, clip_height).translate(
        (clip_width / 2 + tab_length / 2, 0, 0)
    )

    return clip.fuse(tab).cut(screw_hole)
