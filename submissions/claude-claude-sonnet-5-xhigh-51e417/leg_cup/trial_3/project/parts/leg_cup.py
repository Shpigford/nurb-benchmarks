from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_clearance=0.4, pocket_depth=8.0, draft=False):
    """
    wall_thickness: how thick the cup's side walls and floor are
    pocket_clearance: extra room the pocket gets over the leg's measured cross-section
    pocket_depth: how far the leg's foot drops into the pocket
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_w = leg_width + pocket_clearance
    pocket_d = leg_depth + pocket_clearance
    outer_w = pocket_w + 2 * wall_thickness
    outer_d = pocket_d + 2 * wall_thickness
    outer_h = lift + pocket_depth

    body = Box(outer_w, outer_d, outer_h)

    top = outer_h / 2
    overshoot = 5.0
    cutter = Pos(0, 0, top - pocket_depth / 2 + overshoot / 2) * Box(
        pocket_w, pocket_d, pocket_depth + overshoot
    )
    body = body - cutter

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and e not in concave
    )
    return polish(body, keep, 1.0)
