from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that seats a short workbench leg and lifts it level.

    The pocket and floor sizes come from measurements.toml (leg_width, leg_depth,
    lift). Walls and pocket depth are the specified 2.0 mm and 8.0 mm.

    lift: how thick the solid floor under the foot is (unmeasured, provisional)
    """
    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0
    inner_w = measured("leg_width") + clearance
    inner_d = measured("leg_depth") + clearance
    lift = measured("lift")
    outer_w = inner_w + 2 * wall
    outer_d = inner_d + 2 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height).move(Location((0, 0, height / 2)))
    pocket = Box(inner_w, inner_d, pocket_depth).move(
        Location((0, 0, lift + pocket_depth / 2))
    )
    cup = body - pocket
    if draft:
        return cup
    # Chamfer only outer edges above the bed so the pocket stays exact and
    # the 2 mm walls are not eaten from both sides.
    bed = cup.bounding_box().min.Z
    outer = cup.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 1e-6)
    inner = concave_edges(cup)
    keep = outer - inner
    return polish(cup, keep, 1.0)
