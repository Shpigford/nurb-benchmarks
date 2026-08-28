from nurb import *


@part
def leg_cup():
    """Slip-over cup that raises one rectangular workbench leg.

    The leg measurements and provisional lift are read from measurements.toml so
    the printed geometry follows the recorded fit values.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_depth_y = leg_depth + clearance
    outside_width = pocket_width + 2.0 * wall_thickness
    outside_depth = pocket_depth_y + 2.0 * wall_thickness

    body = Box(
        outside_width,
        outside_depth,
        lift + pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_depth_y,
        pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0, 0, lift))
    return body - pocket
