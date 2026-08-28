from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
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

    clip_width = channel_width + 2 * wall_thickness
    total_width = clip_width + tab_length
    total_height = base_thickness + channel_depth
    corner = (Align.MIN, Align.MIN, Align.MIN)

    # Start with one rectangular blank, then remove only the open channel and
    # the area above the mounting tab. The result remains one fused solid.
    blank = Box(total_width, part_length, total_height, align=corner)
    channel = Box(channel_width, part_length, channel_depth, align=corner)
    channel = channel.translate((wall_thickness, 0, base_thickness))
    tab_clearance = Box(tab_length, part_length, channel_depth, align=corner)
    tab_clearance = tab_clearance.translate((clip_width, 0, base_thickness))
    screw_hole = Cylinder(
        screw_hole_diameter / 2,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((clip_width + tab_length / 2, part_length / 2, 0))

    return blank - channel - tab_clearance - screw_hole
