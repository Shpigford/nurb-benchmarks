from nurb import *


@part
def tmp_altpolish(
    wall_thickness=2.0,
    pocket_depth=8.0,
    leg_clearance=0.4,
    chamfer_size=1.0,
    draft=False,
):
    """A slip-over cup for the short bench leg: the foot drops in, the solid floor lifts it level.

    wall_thickness: how thick the four side walls around the leg are
    pocket_depth: how far the leg's foot drops down into the cup
    leg_clearance: extra room around the leg so the cup slips on by hand
    chamfer_size: how big a flat is taken off the outside edges
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + leg_clearance
    pocket_depth_y = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_depth = pocket_depth_y + 2 * wall_thickness
    height = lift + pocket_depth

    body = Pos(0, 0, height / 2) * Box(outer_width, outer_depth, height)
    # The pocket runs out through the top so nothing roofs it over.
    mouth = Pos(0, 0, lift + (pocket_depth + 1.0) / 2) * Box(
        pocket_width, pocket_depth_y, pocket_depth + 1.0
    )
    body = body - mouth

    if draft:
        return body

    # The outside corners and the outside of the rim. The pocket mouth stays sharp:
    # a lead-in chamfer there is fit geometry, and the bottom face is the bed.
    tol = 1e-6
    bed = body.bounding_box().min.Z

    def outside(edge):
        b = edge.bounding_box()
        return (
            b.max.X > outer_width / 2 - tol
            or b.min.X < -outer_width / 2 + tol
            or b.max.Y > outer_depth / 2 - tol
            or b.min.Y < -outer_depth / 2 + tol
        )

    keep = body.edges().filter_by(
        lambda e: outside(e) and e.bounding_box().max.Z > bed + tol and e.bounding_box().min.Z < bed + tol
    )
    return polish(body, keep, chamfer_size)
