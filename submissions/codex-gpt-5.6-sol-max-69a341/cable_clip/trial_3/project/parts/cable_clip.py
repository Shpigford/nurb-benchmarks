from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter")):
    """A screw-down clip for an 8 mm cable bundle.

    bundle_diameter: measured width of the cable bundle held by the channel
    """
    clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_width = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    channel_body_width = channel_width + 2.0 * wall_thickness
    overall_height = base_thickness + channel_depth

    channel_body = Box(
        channel_body_width,
        part_length,
        overall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    channel_void = Box(
        channel_width,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).moved(Pos(wall_thickness, 0.0, base_thickness))

    mounting_tab = Box(
        tab_length,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).moved(Pos(channel_body_width, 0.0, 0.0))

    screw_hole = Cylinder(
        screw_hole_width / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Pos(channel_body_width + tab_length / 2.0, part_length / 2.0, 0.0))

    return (channel_body - channel_void + mounting_tab) - screw_hole
