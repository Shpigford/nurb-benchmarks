"""Slip-over workbench foot cup driven by the measurements on file."""

from nurb import *


@part
def leg_cup():
    """An upright rectangular pocket over a solid leveling floor."""
    pocket_width = measured("leg_width") + 0.4
    pocket_depth = measured("leg_depth") + 0.4
    lift = measured("lift")
    wall_thickness = 2.0
    pocket_height = 8.0

    body = Box(
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
    return body - pocket
