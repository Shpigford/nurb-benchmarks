from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter")):
    """A screw-down clip for a cable bundle running along Y.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    channel_clearance = 0.4
    wall_thickness = 2.4
    base_thickness = 3.0
    part_length = 12.0
    tab_length = 10.0
    screw_hole_width = 4.2

    channel_width = bundle_diameter + channel_clearance
    channel_depth = bundle_diameter
    channel_outer_width = channel_width + 2.0 * wall_thickness
    overall_width = channel_outer_width + tab_length

    # Keep the channel centered on X; the tab continues from its +X wall.
    base_center_x = tab_length / 2.0
    left_wall_center_x = -(channel_width + wall_thickness) / 2.0
    right_wall_center_x = (channel_width + wall_thickness) / 2.0
    tab_center_x = channel_outer_width / 2.0 + tab_length / 2.0

    base = Pos(base_center_x, 0, 0) * Box(
        overall_width,
        part_length,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    left_wall = Pos(left_wall_center_x, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    right_wall = Pos(right_wall_center_x, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    body = base + left_wall + right_wall
    screw_hole = Pos(tab_center_x, 0, 0) * Cylinder(
        screw_hole_width / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return body - screw_hole
