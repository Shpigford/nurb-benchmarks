from nurb import *

# The cable bundle this clip holds, from measurements.toml (calipers across the bundle).
BUNDLE = measured("bundle_diameter")


@part
def cable_clip(
    bundle_diameter=BUNDLE,
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    chamfer_size=1.0,
    draft=False,
):
    """Screw-down clip: an open-top channel for a cable bundle with a flat mounting tab.

    bundle_diameter: how thick the cable bundle is; sets the channel width and depth
    cable_clearance: extra width in the channel so the bundle drops in without forcing
    wall_thickness: how thick each channel wall is
    base_thickness: how much plastic sits under the cable, and how thick the tab is
    clip_length: how long the clip is along the cable
    tab_length: how far the mounting tab reaches out from the channel wall
    screw_hole_width: diameter of the screw hole through the tab
    chamfer_size: size of the edge chamfers on the outside of the clip
    """
    if bundle_diameter < 2.0:
        reject(
            f"bundle_diameter {bundle_diameter} is too small for a printed channel: "
            "use 2.0 or more",
            param="bundle_diameter",
        )
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 2mm a printed hole needs: "
            "use 2.0 or more",
            param="screw_hole_width",
        )
    if tab_length < screw_hole_width + 2 * 2.0:
        reject(
            f"tab_length {tab_length} leaves under 2mm beside the {screw_hole_width} "
            f"screw hole: use {screw_hole_width + 4.0:g} or more",
            param="tab_length",
        )
    if clip_length < screw_hole_width + 2 * 2.0:
        reject(
            f"clip_length {clip_length} leaves under 2mm beside the {screw_hole_width} "
            f"screw hole: use {screw_hole_width + 4.0:g} or more",
            param="clip_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    height = base_thickness + channel_depth
    body_width = 2 * wall_thickness + channel_width
    corner = (Align.MIN, Align.MIN, Align.MIN)

    # The channel body and the tab, sharing the bed. The cable lies along Y.
    body = Box(body_width, clip_length, height, align=corner)
    tab = Pos(body_width, 0, 0) * Box(tab_length, clip_length, base_thickness, align=corner)
    clip = body + tab

    # Open-top channel with square corners; the cutter overshoots so no face is coplanar.
    channel = Pos(wall_thickness, -1, base_thickness) * Box(
        channel_width, clip_length + 2, channel_depth + 1, align=corner
    )
    clip -= channel

    # Vertical through-hole centred in the tab.
    hole = Pos(body_width + tab_length / 2, clip_length / 2, -1) * Cylinder(
        screw_hole_width / 2, base_thickness + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    clip -= hole

    if draft:
        return clip

    # Polish the outside only. Keep sharp: everything inside the channel (fit geometry),
    # any edge lying in the bed face, the concave junctions, the screw hole rims, and the
    # short horizontal edges in the two end faces. Leaving those last ones sharp means every
    # top corner is two chamfers meeting in a line rather than three meeting in a sliver
    # triangle, and it keeps the channel's inner faces full rectangles.
    eps = 1e-3
    bb_all = clip.bounding_box()
    bed, front, back = bb_all.min.Z, bb_all.min.Y, bb_all.max.Y
    concave = [(e.center(), e.length) for e in concave_edges(clip)]
    inner_x0 = wall_thickness - eps
    inner_x1 = wall_thickness + channel_width + eps

    def is_concave(e):
        c, n = e.center(), e.length
        return any((c - cc).length < eps and abs(n - cn) < eps for cc, cn in concave)

    def exposed(e):
        bb = e.bounding_box()
        flat = bb.max.Z - bb.min.Z < eps
        if bb.max.Z <= bed + eps:
            return False  # lies in the bottom face
        if e.geom_type == GeomType.CIRCLE:
            return False  # screw hole rim
        if bb.min.X >= inner_x0 and bb.max.X <= inner_x1 and bb.min.Z >= base_thickness - eps:
            return False  # inside the channel: walls, floor, and its mouth
        if flat and (bb.max.Y <= front + eps or bb.min.Y >= back - eps):
            return False  # horizontal edge in an end face
        if is_concave(e):
            return False
        return True

    keep = clip.edges().filter_by(exposed)
    return polish(clip, keep, chamfer_size)
