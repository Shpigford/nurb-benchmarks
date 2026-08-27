"""Screw-down cable clip with an open-top, square-corner channel."""

from nurb import *


@part
def cable_clip(bundle_diameter: float = measured("bundle_diameter")):
    """Screw-down clip for a cable bundle.

    bundle_diameter: diameter of the cable bundle held by the channel
    """
    channel_clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    tab_length = 10.0
    part_length = 12.0
    mounting_hole_diameter = 4.2

    channel_inner_width = bundle_diameter + channel_clearance
    channel_outer_width = channel_inner_width + 2.0 * wall_thickness
    overall_width = channel_outer_width + tab_length
    channel_wall_height = bundle_diameter

    # The base is the channel floor plus the flush mounting tab.  Keeping it
    # one rectangle makes the bottom a single uninterrupted bed face.
    base = Box(
        overall_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    left_wall = Pos(0, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_wall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    right_wall = Pos(channel_outer_width - wall_thickness, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_wall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    clip = base + left_wall + right_wall

    # Cut past both faces so the mounting hole is unambiguously through the
    # 3 mm tab while its centre remains at the tab's exact centre.
    hole = Pos(
        channel_outer_width + tab_length / 2.0,
        part_length / 2.0,
        -1.0,
    ) * Cylinder(
        mounting_hole_diameter / 2.0,
        base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Deliberately retain square channel and exterior corners: they are
    # dimension-critical and the requested nominal volume leaves no cosmetic
    # material to remove.
    return clip - hole
