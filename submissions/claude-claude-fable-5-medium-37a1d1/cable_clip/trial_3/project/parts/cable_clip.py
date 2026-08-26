from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    wall_thickness=2.4,
    base_thickness=3.0,
    length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    draft=False,
):
    """A screw-down clip: an open-top channel for a cable bundle with a flat mounting tab.

    bundle_diameter: how thick the cable bundle is; the channel is sized from it
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    length: how long the clip is along the cable
    tab_length: how far the mounting tab sticks out beside the channel
    screw_hole_width: diameter of the screw hole in the tab
    """
    channel_width = bundle_diameter + 0.4
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth

    if screw_hole_width + 2.0 > tab_length:
        reject(
            f"screw_hole_width {screw_hole_width} leaves under 1mm of tab each side: "
            f"shorten it below {tab_length - 2.0} or lengthen the tab",
            param="screw_hole_width",
        )

    body = Pos(body_width / 2, 0, height / 2) * Box(body_width, length, height)
    channel = Pos(body_width / 2, 0, base_thickness + channel_depth / 2 + 0.5) * Box(
        channel_width, length + 2, channel_depth + 1
    )
    body = body - channel

    tab_x = body_width + tab_length / 2
    tab = Pos(tab_x, 0, base_thickness / 2) * Box(tab_length, length, base_thickness)
    hole = Pos(tab_x, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + 2
    )
    clip = body + tab - hole

    if draft:
        return clip

    concave = concave_edges(clip)
    inner_lo = wall_thickness + 1e-3
    inner_hi = wall_thickness + channel_width - 1e-3

    def keep_edge(e):
        bb = e.bounding_box()
        if bb.min.Z <= 1e-3:
            return False  # lies in the bed face
        if e.length < 3.0:
            return False  # a 2.4mm wall top: three chamfers meeting there leave a sliver
        if any(e.is_same(c) for c in concave):
            return False
        # nothing inside the channel: edges whose span lies within the channel walls
        if bb.min.X >= inner_lo - 0.01 and bb.max.X <= inner_hi + 0.01 and bb.min.Z >= base_thickness - 1e-3:
            return False
        # the top rim of the channel must stay sharp: no lead-in on a fit
        if abs(bb.min.X - inner_lo) < 0.01 or abs(bb.max.X - inner_hi) < 0.01:
            if bb.min.Z > base_thickness:
                return False
        # leave the screw hole rim alone
        if bb.min.X > body_width + 1e-3 and bb.max.X < body_width + tab_length - 1e-3:
            return False
        return True

    keep = clip.edges().filter_by(keep_edge)
    return polish(clip, keep, 1.0)
