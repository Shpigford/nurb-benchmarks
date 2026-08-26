from nurb import *


@part
def cable_clip(
    bundle_diameter=8.0,
    draft=False,
):
    """Screw-down clip for a taped cable bundle.

    bundle_diameter: measured across the cable bundle; sets channel depth
        and (plus 0.4 mm clearance) inner width.
    """
    clearance = 0.4
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    hole_dia = 4.2

    channel_width = bundle_diameter + clearance
    channel_depth = bundle_diameter
    body_w = wall + channel_width + wall
    total_w = body_w + tab_length
    hole_x = tab_length / 2
    hole_y = length / 2

    slab = Pos(total_w / 2, length / 2, base / 2) * Box(total_w, length, base)
    left = Pos(tab_length + wall / 2, length / 2, base + channel_depth / 2) * Box(
        wall, length, channel_depth
    )
    right = Pos(
        tab_length + wall + channel_width + wall / 2,
        length / 2,
        base + channel_depth / 2,
    ) * Box(wall, length, channel_depth)
    body = slab + left + right

    hole = Pos(hole_x, hole_y, base / 2) * Cylinder(hole_dia / 2, base + 2)
    body = body - hole

    if draft:
        return body

    x0 = tab_length + wall
    x1 = x0 + channel_width
    z0 = base
    bed = body.bounding_box().min.Z

    def in_channel(e):
        bb = e.bounding_box()
        cx = (bb.min.X + bb.max.X) / 2
        cz = (bb.min.Z + bb.max.Z) / 2
        return (x0 - 0.05) <= cx <= (x1 + 0.05) and cz >= (z0 - 0.05)

    def keep_edge(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        if in_channel(e):
            return False
        # Leave Y-end faces square so corner chamfers do not make slivers.
        if (bb.max.Y - bb.min.Y) < 0.5:
            return False
        cx = (bb.min.X + bb.max.X) / 2
        cy = (bb.min.Y + bb.max.Y) / 2
        cz = (bb.min.Z + bb.max.Z) / 2
        # Leave the through-hole sharp (3 mm plate, 1 mm chamfer would starve the wall).
        if (
            abs(cx - hole_x) < hole_dia
            and abs(cy - hole_y) < hole_dia
            and cz < base + 0.6
        ):
            return False
        # Tab-to-wall junction is concave; do not cosmetic-chamfer it.
        if abs(cx - tab_length) < 0.6 and abs(cz - base) < 1.2:
            return False
        return True

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
