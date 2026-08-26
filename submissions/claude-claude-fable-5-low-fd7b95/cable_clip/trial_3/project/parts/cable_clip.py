from nurb import *

EPS = 1e-6


@part
def cable_clip(bundle_diameter=8.0, draft=False):
    """Screw-down cable clip: open-top channel with a screw tab.

    bundle_diameter: how wide the cable bundle is across
    """
    if bundle_diameter < 2.0:
        reject(
            "bundle_diameter under 2mm leaves a channel too small to print: raise it",
            param="bundle_diameter",
        )

    channel_width = bundle_diameter + 0.4   # snug fit slack on the opening
    channel_depth = bundle_diameter
    wall = 2.4
    base = 3.0
    length = 12.0
    tab_length = 10.0
    tab_thickness = 3.0
    screw_hole = 4.2

    body_width = channel_width + 2 * wall
    height = base + channel_depth

    body = Box(body_width, length, height,
               align=(Align.MIN, Align.CENTER, Align.MIN))
    tab = Pos(body_width, 0, 0) * Box(tab_length, length, tab_thickness,
                                      align=(Align.MIN, Align.CENTER, Align.MIN))
    channel = Pos(wall, 0, base) * Box(channel_width, length, channel_depth + 1,
                                       align=(Align.MIN, Align.CENTER, Align.MIN))
    hole = Pos(body_width + tab_length / 2, 0, -1) * Cylinder(
        screw_hole / 2, tab_thickness + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))

    clip = body + tab - channel - hole

    if draft:
        return clip

    # Chamfer exposed convex edges only: nothing on the bed, nothing inside the
    # channel (its walls and floor are fit geometry and stay square), no concave
    # junctions like the tab-to-wall corner.
    concave = set(concave_edges(clip))
    inner_lo = wall - EPS
    inner_hi = wall + channel_width + EPS

    def exposed(e):
        bb = e.bounding_box()
        if bb.min.Z <= EPS or e in concave:
            return False
        # channel interior stays square: it is the fit geometry
        if bb.min.X >= inner_lo and bb.max.X <= inner_hi:
            return False
        # screw hole rim stays sharp: chamfering it thins the tab around the bore
        if e.geom_type == GeomType.CIRCLE:
            return False
        # wall corners rising off the tab: chamfering them slivers against the tab top
        if abs(bb.min.X - body_width) < EPS and bb.min.Z > tab_thickness - EPS:
            return False
        return True

    keep = clip.edges().filter_by(exposed)
    return polish(clip, keep, 1.0)
