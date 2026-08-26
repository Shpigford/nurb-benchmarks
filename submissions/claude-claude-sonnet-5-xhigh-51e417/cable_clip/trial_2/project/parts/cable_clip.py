from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    wall_thickness=2.4,
    base_thickness=3.0,
    part_length=12.0,
    tab_length=10.0,
    tab_hole_diameter=4.2,
    draft=False,
):
    """
    bundle_diameter: how thick the cable bundle is, across
    wall_thickness: how thick each channel wall is
    base_thickness: how thick the solid base under the channel is
    part_length: how long the clip is along the cable
    tab_length: how far the mounting tab reaches out from the channel wall
    tab_hole_diameter: the screw hole through the mounting tab
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    block_width = channel_width + 2 * wall_thickness
    total_width = tab_length + block_width

    channel_x_min = tab_length + wall_thickness
    channel_x_max = channel_x_min + channel_width
    total_height = base_thickness + channel_depth

    base = Box(total_width, part_length, base_thickness, align=(Align.MIN, Align.MIN, Align.MIN))

    near_wall = Box(wall_thickness, part_length, channel_depth, align=(Align.MIN, Align.MIN, Align.MIN))
    near_wall = Pos(tab_length, 0, base_thickness) * near_wall

    far_wall = Box(wall_thickness, part_length, channel_depth, align=(Align.MIN, Align.MIN, Align.MIN))
    far_wall = Pos(channel_x_max, 0, base_thickness) * far_wall

    body = base + near_wall + far_wall

    hole = Cylinder(
        tab_hole_diameter / 2,
        base_thickness * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    hole = Pos(tab_length / 2, part_length / 2, base_thickness / 2) * hole
    body = body - hole

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = concave_edges(body)

    def in_channel(edge):
        bb = edge.bounding_box()
        within_x = bb.min.X >= channel_x_min - 1e-6 and bb.max.X <= channel_x_max + 1e-6
        at_or_above_floor = bb.min.Z >= base_thickness - 1e-6
        return within_x and at_or_above_floor

    def wall_top_end_edge(edge):
        # The short top-rim segment at each wall's Y end: skip it so only two
        # chamfers (not three) meet at the wall's top-outer corner.
        bb = edge.bounding_box()
        at_top = abs(bb.min.Z - total_height) < 1e-6 and abs(bb.max.Z - total_height) < 1e-6
        at_end = (abs(bb.min.Y) < 1e-6 and abs(bb.max.Y) < 1e-6) or (
            abs(bb.min.Y - part_length) < 1e-6 and abs(bb.max.Y - part_length) < 1e-6
        )
        return at_top and at_end

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-6
        and e.geom_type != GeomType.CIRCLE
        and e not in concave
        and not in_channel(e)
        and not wall_top_end_edge(e)
    )

    return polish(body, keep, 1.0)
