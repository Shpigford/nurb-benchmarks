from nurb import *


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),  # 8.0, calipers, on file
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    chamfer_size=1.0,
    draft=False,
):
    """A screw-down clip that traps a cable bundle in an open-top channel.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: how much wider than the bundle the channel is cut
    wall_thickness: how thick each channel wall is
    base_thickness: how much material sits under the cable, and how thick the tab is
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab sticks out past the wall
    screw_hole_width: how wide the screw hole through the tab is
    chamfer_size: how much is taken off the exposed outside edges
    """
    if bundle_diameter <= 0:
        reject(
            "bundle_diameter has to be a real cable width; try 8.0",
            param="bundle_diameter",
        )
    if screw_hole_width < 2.0:
        reject(
            f"screw_hole_width {screw_hole_width} prints as a smear below 2mm: "
            "raise it to at least 2.0",
            param="screw_hole_width",
        )
    if screw_hole_width + 4.0 > tab_length:
        reject(
            f"tab_length {tab_length} leaves under 2mm of material around a "
            f"{screw_hole_width}mm hole: raise it above {screw_hole_width + 4.0}",
            param="tab_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    tab_x = body_width + tab_length / 2

    body = Pos(body_width / 2, 0, height / 2) * Box(body_width, clip_length, height)
    # Cut the channel open at the top and at both ends: oversize the cutter everywhere
    # except across its width, which is the one dimension the cable has to fit.
    channel = Pos(body_width / 2, 0, base_thickness + channel_depth) * Box(
        channel_width, clip_length + 4.0, 2 * channel_depth
    )
    tab = Pos(tab_x, 0, base_thickness / 2) * Box(tab_length, clip_length, base_thickness)
    screw_hole = Pos(tab_x, 0, base_thickness / 2) * Cylinder(
        screw_hole_width / 2, 3 * base_thickness
    )

    solid = body - channel + tab - screw_hole
    if draft:
        return solid

    # Keep sharp: everything at or above the channel floor that meets the channel's
    # width (its mouth, its inner walls, its floor), the screw bore, and anything
    # lying in the bed face.
    bed = solid.bounding_box().min.Z
    tol = 1e-6
    channel_min_x = wall_thickness
    channel_max_x = wall_thickness + channel_width
    tab_outer_x = body_width + tab_length
    bore_min_x = tab_x - screw_hole_width / 2
    bore_max_x = tab_x + screw_hole_width / 2

    # A concave edge is never polished: a chamfer there adds a feather wedge exactly
    # where the tab already carries the load.
    def key(edge):
        box = edge.bounding_box()
        return tuple(round(v, 4) for v in (box.min.X, box.min.Y, box.min.Z,
                                           box.max.X, box.max.Y, box.max.Z))

    inside = {key(e) for e in concave_edges(solid)}

    def exposed(edge):
        box = edge.bounding_box()
        if key(edge) in inside:
            return False
        if box.max.Z <= bed + tol:
            return False
        if (
            box.max.Z >= base_thickness - tol
            and box.max.X >= channel_min_x - tol
            and box.min.X <= channel_max_x + tol
        ):
            return False
        if (
            box.min.X >= bore_min_x - tol
            and box.max.X <= bore_max_x + tol
            and box.min.Y >= -screw_hole_width / 2 - tol
            and box.max.Y <= screw_hole_width / 2 + tol
        ):
            return False
        # The tab's outer vertical corners stay sharp: three chamfers meeting there
        # leave a corner triangle under 1mm2, which is a sliver, not polish.
        if box.min.Z <= bed + tol and box.max.X >= tab_outer_x - tol:
            return False
        return True

    keep = solid.edges().filter_by(exposed)
    return polish(solid, keep, chamfer_size)
