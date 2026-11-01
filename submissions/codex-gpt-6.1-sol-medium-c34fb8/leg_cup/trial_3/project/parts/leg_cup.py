from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over workbench foot cup, printed flat bottom down.

    Fit and floor lift come from measurements.toml on every build.
    """
    pocket_width = measured("leg_width") + 0.4
    pocket_depth = measured("leg_depth") + 0.4
    lift = measured("lift")
    body = Box(
        pocket_width + 4.0, pocket_depth + 4.0, lift + 8.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = Pos(0, 0, lift) * Box(
        pocket_width, pocket_depth, 8.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body - pocket
