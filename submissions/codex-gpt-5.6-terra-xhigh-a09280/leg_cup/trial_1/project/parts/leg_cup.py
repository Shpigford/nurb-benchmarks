from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over leveling cup for one rectangular workbench leg.

    The measured leg section and provisional lift are read from
    measurements.toml so a later confirmed lift rebuilds the cup exactly.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0
    inner_width = leg_width + clearance
    inner_depth = leg_depth + clearance

    outer = Box(
        inner_width + 2 * wall_thickness,
        inner_depth + 2 * wall_thickness,
        lift + pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Box(
        inner_width,
        inner_depth,
        pocket_depth + 1.0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, wall_thickness, lift))

    return outer - pocket
