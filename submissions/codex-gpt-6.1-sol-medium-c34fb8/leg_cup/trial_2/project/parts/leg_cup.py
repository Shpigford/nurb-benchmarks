from nurb import *


@part
def leg_cup():
    """Slip-over bench foot with a measured solid lift and an open pocket."""
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")
    if leg_width <= 0 or leg_depth <= 0 or lift <= 0:
        reject("Leg width, leg depth, and lift must all be greater than zero.")

    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    wall_thickness = 2.0
    pocket_height = 8.0

    outside = Box(
        pocket_width + 2 * wall_thickness,
        pocket_depth + 2 * wall_thickness,
        lift + pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth,
        pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # All edges bound exact fit, floor, or full-height wall dimensions.
    # A chamfer here would change those specified dimensions.
    return outside - pocket
