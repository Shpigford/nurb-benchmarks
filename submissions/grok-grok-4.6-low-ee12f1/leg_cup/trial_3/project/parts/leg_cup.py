from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that lifts a short workbench leg level.

    Reads leg_width, leg_depth, and lift from measurements.toml so the
    pocket and floor track the file, including a later caliper on lift.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    inner_w = leg_width + clearance
    inner_d = leg_depth + clearance
    outer_w = inner_w + 2 * wall
    outer_d = inner_d + 2 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Overcut the pocket through the rim so nothing roofs it.
    pocket = Box(
        inner_w,
        inner_d,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pocket = pocket.move(Location((0, 0, lift)))
    cup = body - pocket
    if draft:
        return cup
    return cup
