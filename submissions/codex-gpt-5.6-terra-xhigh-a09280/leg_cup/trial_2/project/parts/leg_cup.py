from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over workbench leg cup.

    lift: floor thickness that raises the short leg; read from measurements.toml.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall_thickness = 2.0
    pocket_clearance = 0.4
    pocket_height = 8.0

    pocket_width = leg_width + pocket_clearance
    pocket_depth = leg_depth + pocket_clearance
    outer_width = pocket_width + 2.0 * wall_thickness
    outer_depth = pocket_depth + 2.0 * wall_thickness

    body = Box(
        outer_width,
        outer_depth,
        lift + pocket_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_depth,
        pocket_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).translate((wall_thickness, wall_thickness, lift))

    return body - pocket
