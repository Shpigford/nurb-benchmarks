from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that lifts a short workbench leg until the wobble is gone.

    The pocket is the measured leg plus 0.4 mm of slip clearance on each inner
    span. Walls are 2 mm all around. The solid floor is `lift` thick so an
    unmeasured shim height can be swapped in measurements.toml without
    touching this file.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    slip = 0.4
    wall = 2.0
    pocket_depth = 8.0

    inner_w = leg_width + slip
    inner_d = leg_depth + slip
    outer_w = inner_w + 2.0 * wall
    outer_d = inner_d + 2.0 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height).moved(Location((0, 0, height / 2)))
    pocket = Box(inner_w, inner_d, pocket_depth).moved(
        Location((0, 0, lift + pocket_depth / 2))
    )
    cup = body - pocket
    if draft:
        return cup
    return cup
