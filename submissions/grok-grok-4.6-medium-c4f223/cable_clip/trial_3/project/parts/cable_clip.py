from nurb import *

# Screw-down clip for a taped cable bundle. Fit numbers that are not
# bundle size stay fixed so nearby bundle diameters only grow the channel.
_CLEARANCE = 0.4
_WALL = 2.4
_BASE = 3.0
_LENGTH = 12.0
_TAB = 10.0
_TAB_THICK = 3.0
_HOLE = 4.2


@part
def cable_clip(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Screw-down cable clip: open channel along Y, mounting tab on +X.

    bundle_diameter: measured width of the cable bundle; sets channel width
    (plus 0.4 mm clearance) and channel depth.
    """
    channel_w = bundle_diameter + _CLEARANCE
    channel_d = bundle_diameter
    outer_w = channel_w + 2 * _WALL
    height = _BASE + channel_d

    body = Box(outer_w, _LENGTH, height, align=(Align.MIN, Align.MIN, Align.MIN))
    # Oversize the cut so the channel is open the full length and has no film.
    cut = Box(
        channel_w,
        _LENGTH + 2,
        channel_d + 1,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    cut = cut.move(Location((_WALL, -1, _BASE)))
    channel = body - cut

    tab = Box(_TAB, _LENGTH, _TAB_THICK, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = tab.move(Location((outer_w, 0, 0)))
    clip = channel + tab

    hole = Cylinder(_HOLE / 2, _TAB_THICK + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hole = hole.move(Location((outer_w + _TAB / 2, _LENGTH / 2, -1)))
    clip = clip - hole

    if draft:
        return clip

    bed = clip.bounding_box().min.Z
    concave = concave_edges(clip)
    channel_x0 = _WALL
    channel_x1 = _WALL + channel_w

    def keep_edge(e):
        bb = e.bounding_box()
        # Edges that lie in the bed, not merely touch it.
        if bb.max.Z <= bed + 1e-4:
            return False
        # Circular screw hole.
        if bb.size.X > 0.5 and abs(bb.size.X - bb.size.Y) < 1e-4 and bb.size.Z < 1e-4:
            return False
        # Vertical edges: chamfering them with the top edges leaves a 0.87mm2
        # corner triangle, which check reports as a sliver.
        if bb.size.Z > 0.5 and bb.size.X < 1e-4 and bb.size.Y < 1e-4:
            return False
        # Channel interior: floor and inner walls. Leave those square.
        in_x = bb.min.X >= channel_x0 - 1e-4 and bb.max.X <= channel_x1 + 1e-4
        on_inner = (
            abs(bb.min.X - channel_x0) < 1e-4
            or abs(bb.max.X - channel_x1) < 1e-4
            or abs(bb.min.X - channel_x1) < 1e-4
            or abs(bb.max.X - channel_x0) < 1e-4
        )
        if (in_x or on_inner) and bb.min.Z >= _BASE - 1e-4:
            return False
        return True

    keep = clip.edges().filter_by(keep_edge) - concave
    return polish(clip, keep, 1.0)
