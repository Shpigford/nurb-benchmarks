from nurb import *


@part
def leg_cup(wall=2.0, pocket_depth=8.0, clearance=0.4, draft=False):
    """Slip-over cup that seats a wobbly bench leg and lifts it level.

    wall: how thick the cup wall is on all four sides
    pocket_depth: how far the leg's foot sinks into the pocket
    clearance: extra room the pocket gives the leg over its measured size
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_x = leg_width + clearance
    pocket_y = leg_depth + clearance
    outer_x = pocket_x + 2 * wall
    outer_y = pocket_y + 2 * wall
    outer_z = lift + pocket_depth

    body = Box(outer_x, outer_y, outer_z, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket = Box(pocket_x, pocket_y, pocket_depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket = Pos(0, 0, lift) * pocket
    body -= pocket

    if draft:
        return body

    top = body.bounding_box().max.Z
    concave = concave_edges(body)
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z == top)
    keep = keep.filter_by(lambda e: e not in concave)
    return polish(body, keep, 1.0)
