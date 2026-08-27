from nurb import *


@part
def leg_cup():
    """A slip-over cup that lifts and steadies the workbench's short leg."""
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_depth_y = leg_depth + clearance
    overall_width = pocket_width + 2.0 * wall_thickness
    overall_depth = pocket_depth_y + 2.0 * wall_thickness

    outer = Box(
        overall_width,
        overall_depth,
        lift + pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Pos(wall_thickness, wall_thickness, lift) * Box(
        pocket_width,
        pocket_depth_y,
        pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    return outer - pocket
