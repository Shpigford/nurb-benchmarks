from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """A screw-down, open-top clip for an 8 mm cable bundle.

    bundle_diameter: measured diameter of the cable bundle held in the channel.
    """
    wall_thickness = 2.4
    base_thickness = 3.0
    channel_clearance = 0.4
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    clip_width = channel_width + 2.0 * wall_thickness
    total_height = base_thickness + channel_depth

    # The U-channel is cut through the full Y length, retaining an exactly flat,
    # square-cornered floor and vertical fit walls.
    clip = Box(
        clip_width,
        part_length,
        total_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    channel = Box(
        channel_width,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, 0.0, base_thickness))
    body = clip - channel

    # The tiny overlap fuses the tab to the base without changing its 10 mm
    # extension beyond the outside wall.
    fuse_overlap = 0.01
    tab = Box(
        tab_length + fuse_overlap,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((clip_width - fuse_overlap, 0.0, 0.0))
    body = body + tab

    hole = Cylinder(
        screw_hole_diameter / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((clip_width + tab_length / 2.0, part_length / 2.0, 0.0))
    return body - hole
