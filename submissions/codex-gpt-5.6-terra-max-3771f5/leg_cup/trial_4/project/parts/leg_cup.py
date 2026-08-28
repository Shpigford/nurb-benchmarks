from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over leveling cup sized from the recorded workbench-leg measurements.

    The pocket and exterior remain intentionally sharp: their dimensions are
    fit-critical, including the 2 mm walls and flat lifting floor.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_height = 8.0

    pocket_width = leg_width + clearance
    pocket_depth = leg_depth + clearance
    outer_width = pocket_width + 2.0 * wall_thickness
    outer_depth = pocket_depth + 2.0 * wall_thickness

    on_floor = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(outer_width, outer_depth, lift + pocket_height, align=on_floor)
    pocket = Box(pocket_width, pocket_depth, pocket_height, align=on_floor).translate(
        (0, 0, lift)
    )
    return body - pocket
