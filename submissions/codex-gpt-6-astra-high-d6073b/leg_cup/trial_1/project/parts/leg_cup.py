from nurb import *


@part
def leg_cup():
    """A straight-sided workbench foot cup with a measured lifting floor."""
    pocket_width = measured("leg_width") + 0.4
    pocket_depth = measured("leg_depth") + 0.4
    lift = measured("lift")
    wall_thickness = 2.0
    pocket_height = 8.0

    body = Box(
        pocket_width + 2.0 * wall_thickness,
        pocket_depth + 2.0 * wall_thickness,
        lift + pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth,
        pocket_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # All edges define specified fit, wall, or floor dimensions. Chamfering
    # them would reduce the required full-height walls or alter the pocket.
    return body - pocket
