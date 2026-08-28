from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    chamfer_size=1.1,
    draft=False,
):
    """Screw-down clip: the bundle drops into the open channel, one screw holds it.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: extra channel width so the bundle drops in without forcing
    wall_thickness: how thick each channel wall is
    base_thickness: material under the cable, and the thickness of the screw tab
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab reaches out sideways
    screw_hole_width: width of the screw hole through the tab
    chamfer_size: how much is taken off the outside edges
    """
    if bundle_diameter <= 0:
        reject("bundle_diameter must be a real measurement across the bundle",
               param="bundle_diameter")
    if screw_hole_width < 2.0:
        raise_dia = "a hole under 2mm prints as a smear; raise screw_hole_width above 2.0"
        reject(f"screw_hole_width {screw_hole_width} is under the 2mm printable bore: {raise_dia}",
               param="screw_hole_width")
    if tab_length < screw_hole_width + 2 * wall_thickness:
        reject(
            f"tab_length {tab_length} leaves under {wall_thickness}mm of tab around a "
            f"{screw_hole_width}mm hole: raise it above "
            f"{screw_hole_width + 2 * wall_thickness}",
            param="tab_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    tab_start = body_width
    hole_x = tab_start + tab_length / 2
    mid_y = clip_length / 2

    body = Pos(body_width / 2, mid_y, height / 2) * Box(body_width, clip_length, height)
    # Open top and both ends: oversized in +z and in y so the cut leaves no coincident face.
    channel = Pos(body_width / 2, mid_y, base_thickness + channel_depth) * Box(
        channel_width, clip_length + 4, 2 * channel_depth
    )
    tab = Pos(tab_start + tab_length / 2, mid_y, base_thickness / 2) * Box(
        tab_length, clip_length, base_thickness
    )
    hole = Pos(hole_x, mid_y, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, base_thickness + 4
    )

    solid = (body + tab) - channel - hole
    if draft:
        return solid

    tol = 1e-6
    bed = solid.bounding_box().min.Z
    concave = concave_edges(solid)
    hole_r = screw_hole_width / 2

    def polishable(e):
        bb = e.bounding_box()
        if e in concave:
            return False  # a chamfer on an inside corner is a feather edge, never relief
        if bb.max.Z <= bed + tol:
            return False  # lies in the bed-contact face
        # The channel is what the cable beds against, so nothing that reaches it gets
        # polished: floor, both inner walls, the mouth they rise to, and the wall-top
        # cross edges, whose chamfer would land on the inner wall face and nick it.
        if (
            bb.max.X >= wall_thickness - tol
            and bb.min.X <= wall_thickness + channel_width + tol
            and bb.max.Z >= base_thickness - tol
        ):
            return False
        # The screw bore stays the size the table says it is.
        if (
            abs(bb.min.X - (hole_x - hole_r)) < tol
            and abs(bb.max.X - (hole_x + hole_r)) < tol
        ):
            return False
        return True

    keep = solid.edges().filter_by(polishable)
    return polish(solid, keep, chamfer_size)
