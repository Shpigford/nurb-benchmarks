from nurb import *


@part
def leg_cup(clearance=0.4, wall=2.0, pocket_depth=8.0, draft=False):
    """A slip-over foot cup that lifts a short bench leg level.

    clearance: total extra pocket width so the leg drops in by hand
    wall: how thick the cup's sides are
    pocket_depth: how deep the leg sits in the cup
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_w = leg_width + clearance
    pocket_d = leg_depth + clearance
    outer_w = pocket_w + 2 * wall
    outer_d = pocket_d + 2 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket = Pos(0, 0, lift) * Box(
        pocket_w, pocket_d, pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - pocket

    if draft:
        return body

    # Only the four outer vertical corners get the polish chamfer: the rim and
    # pocket mouth are fit-critical mating geometry, and the bottom sits on the bed.
    corners = body.edges().filter_by(Axis.Z).filter_by(
        lambda e: abs(e.bounding_box().min.X) > pocket_w / 2
    )
    return polish(body, corners, 1.0)
