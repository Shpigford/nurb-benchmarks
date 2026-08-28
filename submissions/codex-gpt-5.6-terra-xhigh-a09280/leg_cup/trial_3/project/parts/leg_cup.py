from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over leveling cup for a rectangular workbench leg.

    The leg dimensions and the unmeasured lift are read from measurements.toml.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall_thickness = 2.0
    leg_clearance = 0.4
    pocket_depth = 8.0

    pocket_width = leg_width + leg_clearance
    pocket_depth_size = leg_depth + leg_clearance
    overall_width = pocket_width + (2.0 * wall_thickness)
    overall_depth = pocket_depth_size + (2.0 * wall_thickness)
    overall_height = lift + pocket_depth

    outer = Box(
        overall_width,
        overall_depth,
        overall_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_depth_size,
        pocket_depth + 0.01,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, wall_thickness, lift))

    return outer.cut(pocket)
