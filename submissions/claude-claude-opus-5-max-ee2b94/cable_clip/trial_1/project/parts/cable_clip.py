from nurb import *


def _edge_key(edge):
    """A stable identity for an edge of one built solid, so sets of them compare."""
    bb = edge.bounding_box()
    return tuple(
        round(v, 3)
        for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)
    )


@part
def cable_clip(
    bundle_diameter=measured("bundle_diameter"),
    cable_clearance=0.4,
    wall_thickness=2.4,
    base_thickness=3.0,
    clip_length=12.0,
    tab_length=10.0,
    screw_hole_width=4.2,
    chamfer_size=1.2,
    draft=False,
):
    """Screw-down cable clip: the bundle drops into an open channel, one screw holds it.

    bundle_diameter: how thick the cable bundle is across
    cable_clearance: how much wider than the bundle the channel is cut
    wall_thickness: how thick each of the two channel walls is
    base_thickness: how much material sits under the cable, and how thick the tab is
    clip_length: how far the clip runs along the cable
    tab_length: how far the screw tab reaches out past the wall
    screw_hole_width: diameter of the screw hole through the tab
    chamfer_size: how big the chamfers on the exposed edges are
    """
    if bundle_diameter < 2.0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves a channel a nozzle cannot lay "
            "cleanly: raise it above 2.0",
            param="bundle_diameter",
        )
    if tab_length - screw_hole_width < 4.0:
        reject(
            f"tab_length {tab_length} leaves under 2mm of tab beside a "
            f"{screw_hole_width}mm hole: raise it above {screw_hole_width + 4.0}",
            param="tab_length",
        )

    channel_width = bundle_diameter + cable_clearance
    channel_depth = bundle_diameter
    body_width = channel_width + 2 * wall_thickness
    height = base_thickness + channel_depth
    over = 1.0  # run cuts past the surface so they leave no skin

    corner = (Align.MIN, Align.MIN, Align.MIN)
    body = Box(body_width, clip_length, height, align=corner)
    body += Pos(body_width, 0, 0) * Box(
        tab_length, clip_length, base_thickness, align=corner
    )

    # Square-cornered open channel: straight through in Y, straight out the top.
    body -= Pos(wall_thickness, -over, base_thickness) * Box(
        channel_width, clip_length + 2 * over, channel_depth + over, align=corner
    )

    hole_x = body_width + tab_length / 2
    hole_y = clip_length / 2
    hole_r = screw_hole_width / 2
    body -= Pos(hole_x, hole_y, -over) * Cylinder(
        hole_r, base_thickness + 2 * over, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    if draft:
        return body

    # Name what must stay sharp, then let `polish` chamfer whatever the kernel takes.
    bed = body.bounding_box().min.Z
    concave = {_edge_key(e) for e in concave_edges(body)}
    eps = 1e-6

    def keepable(edge):
        bb = edge.bounding_box()
        if bb.max.Z <= bed + eps:
            return False  # lies in the bed face
        if _edge_key(edge) in concave:
            return False  # a chamfer on an inside corner is a feather edge
        if (
            bb.max.X > wall_thickness - eps
            and bb.min.X < wall_thickness + channel_width + eps
            and bb.min.Z > base_thickness - eps
        ):
            return False  # anything landing on the channel: floor flat, walls square
        if (
            bb.min.X > hole_x - hole_r - eps
            and bb.max.X < hole_x + hole_r + eps
            and bb.min.Y > hole_y - hole_r - eps
            and bb.max.Y < hole_y + hole_r + eps
        ):
            return False  # the bore keeps its modelled diameter top to bottom

        return True

    return polish(body, body.edges().filter_by(keepable), chamfer_size)
