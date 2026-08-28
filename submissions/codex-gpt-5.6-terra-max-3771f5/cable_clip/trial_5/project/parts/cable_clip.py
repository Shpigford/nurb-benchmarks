from nurb import *


@part
def cable_clip(bundle_diameter: float = measured("bundle_diameter")):
    """A screw-down, open-top clip for one cable bundle.

    bundle_diameter: measured diameter of the cable bundle the channel holds.
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    wall_thickness = 2.4
    base_thickness = 3.0
    channel_clearance = 0.4
    part_length = 12.0
    mounting_tab_length = 10.0
    screw_hole_diameter = 4.2

    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    clip_width = channel_width + 2.0 * wall_thickness
    clip_height = base_thickness + channel_depth

    # The U-shaped body holds the bundle.  Its cutter reaches just beyond the
    # top and both ends so the channel is genuinely open along its full length.
    body = Box(
        clip_width,
        part_length,
        clip_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    channel = Box(
        channel_width,
        part_length + 0.2,
        channel_depth + 0.1,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, -0.1, base_thickness))
    clip = body - channel

    # The tab's 0.01 mm overlap makes the face-to-face joint a robust single
    # fused solid while leaving exactly 10.0 mm of tab outside the wall.
    tab = Box(
        mounting_tab_length + 0.01,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((-mounting_tab_length, 0.0, 0.0))
    solid = clip + tab

    screw_hole = Cylinder(
        screw_hole_diameter / 2.0,
        base_thickness + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((-mounting_tab_length / 2.0, part_length / 2.0, -0.1))
    return solid - screw_hole
