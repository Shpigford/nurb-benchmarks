from nurb import *


@part
def leg_cup(
    leg_width=measured("leg_width"),
    leg_depth=measured("leg_depth"),
    lift=measured("lift"),
):
    """Slip-over foot cup for leveling a rectangular workbench leg.

    leg_width: width of the leg pocket
    leg_depth: depth of the leg pocket
    lift: solid floor thickness that raises the bench
    """
    outer = Box(
        leg_width + 4.4,
        leg_depth + 4.4,
        lift + 8.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        leg_width + 0.4,
        leg_depth + 0.4,
        8.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return outer - pocket
