from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter")):
    """A screw-down clip for a cable bundle running along Y.

    bundle_diameter: measured width of the cable bundle held by the channel
    """
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_width = 4.2

    if bundle_diameter <= 0.0:
        reject(
            "bundle_diameter must be greater than 0mm",
            param="bundle_diameter",
        )

    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    channel_outer_width = channel_width + 2.0 * wall_thickness
    overall_width = channel_outer_width + tab_length

    # The base and tab are one flat 3mm slab. The tab occupies the final 10mm
    # along X, immediately outside the right channel wall.
    base_and_tab = Box(
        overall_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    left_wall = Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((0.0, 0.0, base_thickness))

    right_wall = Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness + channel_width, 0.0, base_thickness))

    tab_hole = Cylinder(
        screw_hole_width / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate(
        (
            channel_outer_width + tab_length / 2.0,
            part_length / 2.0,
            0.0,
        )
    )

    return base_and_tab + left_wall + right_wall - tab_hole
