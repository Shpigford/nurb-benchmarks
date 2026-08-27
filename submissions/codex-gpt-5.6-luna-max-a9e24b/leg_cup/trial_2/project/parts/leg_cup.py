from nurb import *


@part
def leg_cup():
    """Slip-over foot cup for a rectangular workbench leg.

    leg_width and leg_depth: measured outside dimensions of the leg.
    lift: provisional floor thickness that raises the bench above the floor.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall_thickness = 2.0
    pocket_depth = 8.0
    clearance = 0.4

    outer_width = leg_width + clearance + 2.0 * wall_thickness
    outer_depth = leg_depth + clearance + 2.0 * wall_thickness
    outer_height = lift + pocket_depth

    body = Box(
        outer_width,
        outer_depth,
        outer_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        leg_width + clearance,
        leg_depth + clearance,
        pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return body - pocket
