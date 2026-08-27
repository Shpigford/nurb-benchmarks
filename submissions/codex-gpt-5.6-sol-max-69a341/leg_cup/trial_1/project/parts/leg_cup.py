from nurb import *


@part
def leg_cup(
    leg_width=measured("leg_width"),
    leg_depth=measured("leg_depth"),
    lift=measured("lift"),
):
    """Slip-over cup that lifts the workbench's short leg.

    leg_width: measured width of the rectangular bench leg
    leg_depth: measured depth of the rectangular bench leg
    lift: solid thickness beneath the leg that removes the wobble
    """
    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_length = leg_depth + clearance
    outside_width = pocket_width + 2.0 * wall
    outside_length = pocket_length + 2.0 * wall

    cup = Box(
        outside_width,
        outside_length,
        lift + pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_length,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return cup - pocket
