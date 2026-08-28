from nurb import *


@part
def leg_cup():
    """A slip-over leveling cup for the short rectangular workbench leg."""
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall_thickness = 2.0
    clearance = 0.4
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_length = leg_depth + clearance
    outer_width = pocket_width + 2.0 * wall_thickness
    outer_length = pocket_length + 2.0 * wall_thickness

    outer = Box(
        outer_width,
        outer_length,
        lift + pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_length,
        pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, wall_thickness, lift))

    return outer - pocket
