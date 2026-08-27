from nurb import *


@part
def leg_cup():
    """A slip-over foot cup that lifts and steadies a short workbench leg."""
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    wall_thickness = 2.0
    pocket_height = 8.0

    outer = Box(
        pocket_width + 2.0 * wall_thickness,
        pocket_depth + 2.0 * wall_thickness,
        lift + pocket_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Pos(wall_thickness, wall_thickness, lift) * Box(
        pocket_width,
        pocket_depth,
        pocket_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    return outer - pocket
