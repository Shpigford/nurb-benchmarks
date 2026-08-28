from nurb import *


@part
def leg_cup(
    wall_thickness=2.0,
    pocket_depth=8.0,
    leg_clearance=0.4,
    chamfer_size=1.0,
    draft=False,
):
    """Slip-over foot cup that lifts the bench's short leg until it stops rocking.

    wall_thickness: how thick the four side walls around the leg are
    pocket_depth: how far the leg's foot drops into the cup
    leg_clearance: total slack around the leg so the cup slides on by hand
    chamfer_size: how big the chamfer is on the outside corners
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + leg_clearance
    pocket_breadth = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_breadth = pocket_breadth + 2 * wall_thickness
    height = lift + pocket_depth

    up = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(outer_width, outer_breadth, height, align=up)
    # The cutter pokes out through the top so the mouth is an open rim rather than a
    # pair of coplanar faces. Its floor sits at z=lift, so the solid pad under the
    # foot is the lift itself.
    mouth = Pos(0, 0, lift) * Box(
        pocket_width, pocket_breadth, pocket_depth + 1.0, align=up
    )
    cup = body - mouth

    if draft:
        return cup

    box = cup.bounding_box()
    bed, rim, tol = box.min.Z, box.max.Z, 1e-4
    concave = {_edge_key(e) for e in concave_edges(cup)}

    def exposed(edge):
        span = edge.bounding_box()
        if _edge_key(edge) in concave:
            return False  # never polish an inside corner
        if span.max.Z <= bed + tol:
            return False  # lies in the bed face
        if span.min.Z >= rim - tol:
            return False  # the rim stays square; see the card
        if (
            min(abs(span.min.X), abs(span.max.X)) < outer_width / 2 - tol
            and min(abs(span.min.Y), abs(span.max.Y)) < outer_breadth / 2 - tol
        ):
            return False  # inboard of the outer wall: the pocket mates with the leg
        return True

    return polish(cup, cup.edges().filter_by(exposed), chamfer_size)


def _edge_key(edge):
    return tuple(round(v, 4) for v in edge.center().to_tuple())
