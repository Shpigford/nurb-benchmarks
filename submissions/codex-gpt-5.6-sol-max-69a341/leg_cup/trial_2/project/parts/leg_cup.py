from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that lifts the short workbench leg.

    The leg fit and lift come from measurements.toml so the shop can correct the
    provisional lift without changing this part.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_leg_depth = leg_depth + clearance
    outer_width = pocket_width + 2.0 * wall
    outer_depth = pocket_leg_depth + 2.0 * wall
    outer_height = lift + pocket_depth

    body = Box(
        outer_width,
        outer_depth,
        outer_height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Pos(wall, wall, lift) * Box(
        pocket_width,
        pocket_leg_depth,
        pocket_depth + 1.0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )

    # The exact fit faces and 2 mm rim stay square; cosmetic chamfers would alter
    # the specified pocket, wall thickness, or flat floor contact.
    return body - pocket
