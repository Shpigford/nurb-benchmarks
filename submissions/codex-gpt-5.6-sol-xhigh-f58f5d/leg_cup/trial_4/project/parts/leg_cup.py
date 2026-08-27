from nurb import *


leg_width = measured("leg_width")
leg_depth = measured("leg_depth")
lift = measured("lift")


@part
def leg_cup():
    """A slip-over cup that lifts the short workbench leg level."""
    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_depth_size = leg_depth + clearance
    outside_width = pocket_width + 2.0 * wall
    outside_depth = pocket_depth_size + 2.0 * wall

    body = Box(
        outside_width,
        outside_depth,
        lift + pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth_size,
        pocket_depth + 0.1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return body - pocket
