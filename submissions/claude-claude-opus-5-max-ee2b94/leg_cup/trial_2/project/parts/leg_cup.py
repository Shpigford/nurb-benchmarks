from nurb import *


@part
def leg_cup(
    leg_width=measured("leg_width"),
    leg_depth=measured("leg_depth"),
    lift=measured("lift"),
    pocket_depth=8.0,
    wall_thickness=2.0,
    leg_clearance=0.4,
    chamfer_size=1.2,
    draft=False,
):
    """A cup the short bench leg drops into, lifting it until the bench stops rocking.

    leg_width: the wide side of the bench leg, measured across it
    leg_depth: the narrow side of the bench leg, measured along it
    lift: how far the solid floor raises the leg off the ground
    pocket_depth: how deep the leg sits in the cup before it bottoms out
    wall_thickness: how thick the four walls that grip the leg are
    leg_clearance: total slop across the pocket so the leg slips on by hand
    chamfer_size: how big the chamfers on the outside edges are
    """
    pocket_x = leg_width + leg_clearance
    pocket_y = leg_depth + leg_clearance
    height = lift + pocket_depth

    up = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(pocket_x + 2 * wall_thickness, pocket_y + 2 * wall_thickness, height, align=up)
    # Overshoot the rim so the cut never has to resolve two coplanar top faces.
    body -= Pos(Z=lift) * Box(pocket_x, pocket_y, pocket_depth + 1.0, align=up)

    if draft:
        return body

    # The pocket is the mating surface: no lead-in at its mouth, no relief in its
    # corners. The bed face keeps its full first layer. What is left is the outside
    # of the cup, which is the only part anybody touches.
    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    tol = 1e-6

    def polishable(edge):
        box = edge.bounding_box()
        if box.max.Z <= bed + tol:
            return False  # lies in the bed face
        # Reach from the centreline, since the cup is centred on X and Y. An edge that
        # never gets past a pocket wall is pocket geometry, and the leg mates on it.
        if (max(-box.min.X, box.max.X) <= pocket_x / 2 + tol
                and max(-box.min.Y, box.max.Y) <= pocket_y / 2 + tol):
            return False
        return not any(edge.is_same(c) for c in concave)

    return polish(body, body.edges().filter_by(polishable), chamfer_size)
