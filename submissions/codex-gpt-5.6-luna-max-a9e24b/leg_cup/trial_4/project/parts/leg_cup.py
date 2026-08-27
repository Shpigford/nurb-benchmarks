from nurb import *


@part
def leg_cup():
    """A solid-floor slip-over cup for leveling a rectangular workbench leg.

    The pocket is open at the top and sized from the measured leg with 0.4 mm
    clearance. Its four walls are 2.0 mm thick and its solid floor is the
    provisional lift measurement.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    outer_width = pocket_width + 4.0
    outer_depth = pocket_depth + 4.0
    wall_height = 8.0

    body = Box(
        outer_width,
        outer_depth,
        lift + wall_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth,
        wall_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body - pocket
