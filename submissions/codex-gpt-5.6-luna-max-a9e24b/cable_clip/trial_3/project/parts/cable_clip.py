from nurb import *


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down cable clip with an open channel and one mounting tab.

    bundle_diameter: diameter of the cable bundle held by the channel
    """
    channel_clearance = 0.4
    channel_width = bundle_diameter + channel_clearance
    wall_thickness = 2.4
    base_thickness = 3.0
    channel_depth = bundle_diameter
    part_length = 12.0
    tab_length = 10.0
    screw_hole_diameter = 4.2

    outer_channel_width = channel_width + 2.0 * wall_thickness
    right_wall_start = wall_thickness + channel_width

    base = Box(
        outer_channel_width,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    left_wall = Pos(0, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    right_wall = Pos(right_wall_start, 0, base_thickness) * Box(
        wall_thickness,
        part_length,
        channel_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    tab = Pos(outer_channel_width, 0, 0) * Box(
        tab_length,
        part_length,
        base_thickness,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    body = base + left_wall + right_wall + tab
    screw_hole = Pos(
        outer_channel_width + tab_length / 2.0,
        part_length / 2.0,
        0,
    ) * Cylinder(
        screw_hole_diameter / 2.0,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - screw_hole

    if draft:
        return body

    outer_x_positions = (
        0.0,
        outer_channel_width,
        outer_channel_width + tab_length,
    )

    def is_safe_outer_corner(edge):
        bounds = edge.bounding_box()
        x_span = bounds.max.X - bounds.min.X
        y_span = bounds.max.Y - bounds.min.Y
        z_span = bounds.max.Z - bounds.min.Z
        on_outer_x = any(
            abs(bounds.min.X - x_position) < 1e-6
            for x_position in outer_x_positions
        )
        return x_span < 1e-6 and y_span < 1e-6 and z_span > 1e-6 and on_outer_x

    safe_outer_edges = body.edges().filter_by(is_safe_outer_corner)
    return polish(body, safe_outer_edges, 1.0)
