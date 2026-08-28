from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over leveling cup for a rectangular workbench leg.

    The fit and lift come from measurements.toml so the same model follows a
    corrected leg measurement or a confirmed wobble measurement.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall_thickness = 2.0
    fit_clearance = 0.4
    pocket_depth = 8.0

    pocket_width = leg_width + fit_clearance
    pocket_depth_size = leg_depth + fit_clearance
    overall_width = pocket_width + 2.0 * wall_thickness
    overall_depth = pocket_depth_size + 2.0 * wall_thickness

    body = Box(
        overall_width,
        overall_depth,
        lift + pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_depth_size,
        pocket_depth,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, wall_thickness, lift))

    return body - pocket
