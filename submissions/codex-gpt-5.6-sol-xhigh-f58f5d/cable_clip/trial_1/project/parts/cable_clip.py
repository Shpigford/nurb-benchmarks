from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter")):
    """A screw-down clip for a cable bundle running along Y.

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
    channel_outer_width = channel_width + 2.0 * wall_thickness

    # The base and tab are one flat plate. Its X offset leaves the channel
    # centered at X=0 while the tab projects from the positive-X wall.
    base_and_tab = Pos(tab_length / 2.0, 0, 0) * Box(
        channel_outer_width + tab_length,
        part_length,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    wall_height = base_thickness + channel_depth
    wall_offset = channel_width / 2.0 + wall_thickness / 2.0
    left_wall = Pos(-wall_offset, 0, 0) * Box(
        wall_thickness,
        part_length,
        wall_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    right_wall = Pos(wall_offset, 0, 0) * Box(
        wall_thickness,
        part_length,
        wall_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    screw_center_x = channel_outer_width / 2.0 + tab_length / 2.0
    screw_hole = Pos(screw_center_x, 0, -1.0) * Cylinder(
        screw_hole_width / 2.0,
        base_thickness + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return (base_and_tab + left_wall + right_wall) - screw_hole
