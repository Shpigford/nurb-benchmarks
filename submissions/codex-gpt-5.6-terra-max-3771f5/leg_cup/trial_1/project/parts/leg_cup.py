from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that raises a short rectangular workbench leg.

    The pocket is intentionally left sharp and open so its measured fit and
    the full-height 2 mm walls remain unchanged.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_length = leg_depth + clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_length = pocket_length + 2 * wall_thickness
    total_height = lift + pocket_depth

    body = Box(
        outer_width,
        outer_length,
        total_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_length,
        pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, wall_thickness, lift))
    return body - pocket
