from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    tab_thickness=3.0,
    screw_hole_width=4.2,
    draft=False,
):
    """Screw-down cable clip: an open-top channel the bundle lies in, with a flat screw tab beside it.

    bundle_diameter: how thick the cable bundle is; sets the channel's width and depth
    cable_clearance: extra channel width beyond the bundle so it drops in without forcing
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable
    clip_length: how long the clip is along the cable
    tab_length: how far the screw tab reaches out from the channel wall
    tab_thickness: how thick the screw tab is
    screw_hole_width: diameter of the screw hole through the tab
    """
    if bundle_diameter <= 0:
        reject(
            "bundle_diameter must be above 0: measure the bundle across and set it",
            param="bundle_diameter",
        )
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 2mm a printed hole needs "
            "to open: raise it to 2 or more",
            param="screw_hole_width",
        )
    if tab_length - screw_hole_width < 4.0 - 1e-9:
        reject(
            f"screw_hole_width {screw_hole_width} leaves under 2mm of tab on each side of "
            f"the hole: lengthen tab_length past {screw_hole_width + 4.0:g} or narrow the hole",
            param="tab_length",
        )
    if clip_length - screw_hole_width < 4.0 - 1e-9:
        reject(
            f"screw_hole_width {screw_hole_width} leaves under 2mm of tab in front of and "
            f"behind the hole: lengthen clip_length past {screw_hole_width + 4.0:g}",
            param="clip_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    total_width = body_width + tab_length

    # One profile in the XZ plane, walked round from the bed: the base and the tab as a
    # single slab, and the two channel walls rising off it. Extruded along Y so the
    # channel runs the full length of the clip and the cable lies along Y.
    outline = [
        (0.0, 0.0),
        (total_width, 0.0),
        (total_width, tab_thickness),
        (body_width, tab_thickness),
        (body_width, height),
        (body_width - wall_thickness, height),
        (body_width - wall_thickness, base_thickness),
        (wall_thickness, base_thickness),
        (wall_thickness, height),
        (0.0, height),
    ]
    profile = make_face(Wire.make_polygon([(x, 0.0, z) for x, z in outline], close=True))
    clip = extrude(profile, clip_length, dir=(0, 1, 0))

    # A vertical through-hole centred in the tab; overshoots both faces so the cut is clean.
    hole = Pos(body_width + tab_length / 2, clip_length / 2, tab_thickness / 2) * Cylinder(
        screw_hole_width / 2, tab_thickness + 2.0
    )
    clip = clip - hole

    if draft:
        return clip

    # Polish the top rim only: the horizontal convex edges a hand meets from above. Left
    # alone: the vertical corners (a third chamfer at every corner would leave a sub-mm2
    # sliver triangle where three meet), everything lying in the bed face, every edge that
    # touches the channel (its floor, walls and mouth are the cable's fit surfaces, and the
    # wall-end edges would clip the corners of its inner faces), the screw hole's rim, and
    # every concave junction.
    bed = clip.bounding_box().min.Z
    eps = 1e-3
    concave = concave_edges(clip)

    def touches_channel(e):
        bb = e.bounding_box()
        return (
            bb.max.X >= wall_thickness - eps
            and bb.min.X <= body_width - wall_thickness + eps
            and bb.max.Z >= base_thickness - eps
        )

    def top_rim(e):
        bb = e.bounding_box()
        if bb.max.Z - bb.min.Z > eps:  # vertical: stays square
            return False
        if bb.max.Z <= bed + eps:  # lies in the bed face
            return False
        if touches_channel(e):
            return False
        return not any(e.is_same(c) for c in concave)

    keep = clip.edges().filter_by(GeomType.LINE).filter_by(top_rim)
    return polish(clip, keep, 1.0)
