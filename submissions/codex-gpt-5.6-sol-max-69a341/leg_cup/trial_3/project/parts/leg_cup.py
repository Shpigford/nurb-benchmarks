from nurb import *


@part
def leg_cup():
    """Slip-over cup that raises the short workbench leg.

    The leg dimensions and lift are read from measurements.toml so the cup
    rebuilds directly from the shop measurements.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_depth_xy = leg_depth + clearance
    outer_width = pocket_width + 2.0 * wall
    outer_depth = pocket_depth_xy + 2.0 * wall
    total_height = lift + pocket_depth

    body = Box(
        outer_width,
        outer_depth,
        total_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth_xy,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return body - pocket
