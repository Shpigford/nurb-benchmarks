from nurb import *


@part
def cable_clip(bundle_diameter: float = 8.0):
    """Screw-down open cable-bundle clip.

    bundle_diameter: measured diameter of the cable bundle held in the channel
    """
    channel_clearance = 0.4
    channel_width = bundle_diameter + channel_clearance
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    channel_depth = bundle_diameter
    tab_length = 10.0
    screw_hole_diameter = 4.2

    body_width = channel_width + 2 * wall_thickness
    overall_height = base_thickness + channel_depth

    body = Box(body_width, part_length, overall_height)
    channel = Box(channel_width, part_length, channel_depth).translate(
        (0, 0, base_thickness / 2)
    )
    tab_center_x = body_width / 2 + tab_length / 2
    tab_center_z = -bundle_diameter / 2
    tab = Box(tab_length, part_length, base_thickness).translate(
        (tab_center_x, 0, tab_center_z)
    )
    screw_hole = Cylinder(screw_hole_diameter / 2, base_thickness).translate(
        (tab_center_x, 0, tab_center_z)
    )

    return body.cut(channel).fuse(tab).cut(screw_hole)
