from nurb import *


@part
def cable_clip(
    bundle_diameter=8.0,
    draft=False,
):
    """Screw-down clip for a taped cable bundle.

    bundle_diameter: calipered width of the cable bundle the channel holds
    """
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    hole_dia = 4.2
    channel_w = bundle_diameter + 0.4
    channel_d = bundle_diameter
    channel_outer = channel_w + 2 * wall
    height = base + channel_d

    body = Box(channel_outer, length, height, align=(Align.MIN, Align.MIN, Align.MIN))
    cut = Box(channel_w, length + 2, channel_d + 1, align=(Align.MIN, Align.MIN, Align.MIN))
    cut = cut.moved(Location((wall, -1, base)))
    body = body - cut

    tab = Box(tab_length, length, base, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = tab.moved(Location((channel_outer, 0, 0)))
    body = body + tab

    hole_x = channel_outer + tab_length / 2
    hole_y = length / 2
    hole = Cylinder(hole_dia / 2, base + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hole = hole.moved(Location((hole_x, hole_y, -1)))
    body = body - hole

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def keep_edge(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        if e.length < 8.0:
            return False
        c = bb.center()
        # Channel interior: square floor and walls, no polish inside.
        if wall - 0.2 <= c.X <= wall + channel_w + 0.2:
            return False
        # Wall sitting on the tab: that junction is concave, not cosmetic.
        if abs(c.X - channel_outer) < 0.4 and c.Z < base + 1.5:
            return False
        dx = c.X - hole_x
        dy = c.Y - hole_y
        if (dx * dx + dy * dy) ** 0.5 < hole_dia / 2 + 0.6:
            return False
        return True

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
