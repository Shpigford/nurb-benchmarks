from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
    """A screw-down, open-top clip for a round cable bundle.

    bundle_diameter: measured diameter of the cable bundle held by the channel.
    """
    channel_clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    clip_width = wall_thickness + channel_width + wall_thickness
    total_height = base_thickness + channel_depth

    # Box and Cylinder are centered on their local origin.  The clip body is
    # centered at the origin, so its bottom is -total_height / 2.
    bed_z = -total_height / 2
    base_center_z = bed_z + base_thickness / 2

    # The channel is cut after the tab is joined, leaving a square-cornered,
    # full-length floor exactly 3 mm above the print bed.
    clip = Box(clip_width, part_length, total_height)
    tab = Box(tab_length, part_length, base_thickness).translate(
        (-(clip_width + tab_length) / 2, 0, base_center_z)
    )
    channel = Box(channel_width, part_length, channel_depth).translate(
        (0, 0, bed_z + base_thickness + channel_depth / 2)
    )
    screw_hole = Cylinder(screw_hole_diameter / 2, base_thickness + 2).translate(
        (-(clip_width + tab_length) / 2, 0, base_center_z)
    )

    return clip.fuse(tab).cut(channel).cut(screw_hole)
