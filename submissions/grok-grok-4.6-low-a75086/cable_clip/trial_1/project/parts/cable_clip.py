from nurb import *


@part
def cable_clip(bundle_diameter=8.0, draft=False):
    """Screw-down clip for a taped cable bundle.

    bundle_diameter: measured width of the cable bundle the channel holds
    """
    clearance = 0.4
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    hole_dia = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    channel_span = wall + channel_width + wall
    height = base + channel_depth

    tab = Box(tab_length, length, base).moved(
        Location((tab_length / 2, length / 2, base / 2))
    )
    trough = Box(channel_span, length, height).moved(
        Location((tab_length + channel_span / 2, length / 2, height / 2))
    )
    body = tab + trough

    channel = Box(channel_width, length + 2, channel_depth + 1).moved(
        Location(
            (
                tab_length + wall + channel_width / 2,
                length / 2,
                base + (channel_depth + 1) / 2,
            )
        )
    )
    body -= channel

    hole = Cylinder(hole_dia / 2, base + 2).moved(
        Location((tab_length / 2, length / 2, base / 2))
    )
    body -= hole

    if draft:
        return body

    bed = body.bounding_box().min.Z
    channel_x_min = tab_length + wall - 0.05
    channel_x_max = tab_length + wall + channel_width + 0.05
    channel_z_min = base - 0.05
    forbidden = concave_edges(body)

    def in_channel(edge):
        bb = edge.bounding_box()
        return (
            bb.min.X >= channel_x_min
            and bb.max.X <= channel_x_max
            and bb.min.Z >= channel_z_min
        )

    def skip(edge):
        if edge in forbidden:
            return True
        if edge.geom_type == GeomType.CIRCLE:
            return True
        if edge.length < 8.0:
            return True
        bb = edge.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return True
        if in_channel(edge):
            return True
        return False

    keep = body.edges().filter_by(lambda e: not skip(e))
    return polish(body, keep, 1.0)
