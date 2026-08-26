from nurb import *

WALL = 2.4
BASE = 3.0
LENGTH = 12.0
TAB = 10.0
HOLE = 4.2
CLEARANCE = 0.4


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down clip that holds a cable bundle in an open-top channel.

    bundle_diameter: measured across the cable bundle; the channel is this deep and 0.4 mm wider
    """
    channel_width = bundle_diameter + CLEARANCE
    channel_depth = bundle_diameter
    channel_outer = WALL + channel_width + WALL
    height = BASE + channel_depth

    body = Box(channel_outer, LENGTH, height, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = Box(TAB, LENGTH, BASE, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = tab.moved(Location((channel_outer, 0, 0)))
    body += tab

    void = Box(
        channel_width,
        LENGTH + 2,
        channel_depth + 1,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).moved(Location((WALL, -1, BASE)))
    body -= void

    hole = Cylinder(
        HOLE / 2,
        BASE + 2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((channel_outer + TAB / 2, LENGTH / 2, -1)))
    body -= hole

    # Leave the channel, bed, and hole unchamfered: inner corners must stay
    # square, bed edges would fail bed_bevel, and a 1 mm hole chamfer thins
    # the tab under min_wall.
    if draft:
        return body
    bed = body.bounding_box().min.Z
    inner_lo = WALL
    inner_hi = WALL + channel_width

    def keep(edge):
        bb = edge.bounding_box()
        if bb.min.Z <= bed + 1e-6:
            return False
        if edge.geom_type != GeomType.LINE:
            return False
        if edge.length < LENGTH - 0.5:
            return False
        mid = edge.center()
        if inner_lo - 1e-4 <= mid.X <= inner_hi + 1e-4:
            return False
        # The tab-to-wall step chamfers into a concave strip.
        if abs(mid.X - channel_outer) < 1e-4 and abs(mid.Z - BASE) < 1e-4:
            return False
        return True

    return polish(body, body.edges().filter_by(keep), 1.0)
