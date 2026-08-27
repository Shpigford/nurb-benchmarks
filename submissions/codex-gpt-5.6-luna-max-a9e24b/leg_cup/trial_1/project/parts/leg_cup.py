from nurb import *


@part
def leg_cup():
    """Slip-over foot cup for leveling a rectangular workbench leg.

    leg_width: measured width of the bench leg
    leg_depth: measured depth of the bench leg
    lift: provisional solid floor thickness under the leg pocket
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    pocket_height = 8.0
    wall_thickness = 2.0

    outside = Box(
        pocket_width + 2.0 * wall_thickness,
        pocket_depth + 2.0 * wall_thickness,
        lift + pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth,
        pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return outside - pocket
