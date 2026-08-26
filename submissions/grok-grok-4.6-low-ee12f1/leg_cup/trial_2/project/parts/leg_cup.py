from nurb import *

# Slip-over foot cup: pocket takes the short bench leg, solid floor supplies the lift.


@part
def leg_cup(draft=False):
    """Cup that the short workbench leg drops into, with a solid floor for lift.

    Geometry is driven only by measured leg_width, leg_depth, and lift.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_w = leg_width + clearance
    pocket_d = leg_depth + clearance
    outer_w = pocket_w + 2.0 * wall
    outer_d = pocket_d + 2.0 * wall
    outer_h = lift + pocket_depth

    body = Location((0, 0, outer_h / 2)) * Box(outer_w, outer_d, outer_h)
    # Overshoot the rim so the cut opens the pocket instead of leaving a roof.
    cut_h = pocket_depth + 1.0
    pocket = Location((0, 0, lift + cut_h / 2)) * Box(pocket_w, pocket_d, cut_h)
    cup = body - pocket
    if draft:
        return cup
    return cup
