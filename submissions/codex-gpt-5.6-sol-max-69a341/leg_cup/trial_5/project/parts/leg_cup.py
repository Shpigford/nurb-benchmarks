from nurb import *


@part
def leg_cup(
    leg_width=measured("leg_width"),
    leg_depth=measured("leg_depth"),
    lift=measured("lift"),
):
    """A slip-over cup that lifts the short workbench leg.

    leg_width: measured width of the workbench leg
    leg_depth: measured depth of the workbench leg
    lift: solid thickness that raises the short leg
    """
    pocket_clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + pocket_clearance
    pocket_length = leg_depth + pocket_clearance
    outer_width = pocket_width + 2.0 * wall_thickness
    outer_length = pocket_length + 2.0 * wall_thickness
    total_height = lift + pocket_depth

    body = Box(
        outer_width,
        outer_length,
        total_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Box(
        pocket_width,
        pocket_length,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0.0, 0.0, lift))

    return body - pocket
