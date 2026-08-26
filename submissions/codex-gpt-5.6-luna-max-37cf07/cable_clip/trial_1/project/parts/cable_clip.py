from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down cable clip for a cable bundle.

    bundle_diameter: diameter of the cable bundle held in the channel
    draft: skip optional cosmetic finishing while tuning the geometry
    """
    if bundle_diameter <= 0.0:
        reject("bundle_diameter must be greater than 0 mm", param="bundle_diameter")

    channel_wall = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    channel_width = bundle_diameter + 0.4
    channel_outer_width = channel_width + 2.0 * channel_wall
    channel_height = base_thickness + bundle_diameter

    # All solids use a minimum corner at the origin so the bed is z=0 and
    # the measured dimensions remain direct bounding-box dimensions.
    base = Box(
        channel_outer_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    left_wall = Pos(0.0, 0.0, base_thickness) * Box(
        channel_wall,
        part_length,
        bundle_diameter,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    right_wall = Pos(channel_wall + channel_width, 0.0, base_thickness) * Box(
        channel_wall,
        part_length,
        bundle_diameter,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    mounting_tab = Pos(channel_outer_width, 0.0, 0.0) * Box(
        tab_length,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = base + left_wall + right_wall + mounting_tab

    # The vertical mounting bore is intentionally oversized in Z so it is a
    # true through-hole without relying on coincident cutter faces.
    mounting_hole = Pos(channel_outer_width + tab_length / 2.0, part_length / 2.0, -0.1) * Cylinder(
        4.2 / 2.0,
        base_thickness + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body - mounting_hole
