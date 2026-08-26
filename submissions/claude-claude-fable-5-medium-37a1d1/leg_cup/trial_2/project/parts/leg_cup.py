from nurb import *


@part
def leg_cup(wall=2.0, pocket_depth=8.0, clearance=0.4, draft=False):
    """Slip-over foot cup: the bench leg drops into the pocket, the floor lifts it level.

    wall: thickness of the four walls around the leg
    pocket_depth: how far the leg's foot sinks into the cup
    clearance: total extra on the pocket over the measured leg
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    inner_w = leg_width + clearance
    inner_d = leg_depth + clearance
    outer_w = inner_w + 2 * wall
    outer_d = inner_d + 2 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height)
    bed = body.bounding_box().min.Z
    top = body.bounding_box().max.Z
    pocket = Box(inner_w, inner_d, pocket_depth)
    pocket = pocket.translate((0, 0, top - pocket.bounding_box().min.Z - pocket_depth))
    body = body - pocket
    if draft:
        return body
    # Chamfer only the outside: bottom edges stay sharp on the bed, pocket edges are mating geometry.
    outside = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and (abs(e.bounding_box().max.X) > inner_w / 2 or abs(e.bounding_box().max.Y) > inner_d / 2)
    )
    return polish(body, outside, 1.0)
