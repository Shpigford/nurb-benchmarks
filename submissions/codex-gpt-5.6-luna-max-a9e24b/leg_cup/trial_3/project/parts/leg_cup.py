from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup for leveling a rectangular workbench leg.

    leg_width: measured width of the leg entering the pocket
    leg_depth: measured depth of the leg entering the pocket
    lift: provisional height of the solid floor that raises the bench
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0

    pocket_width = leg_width + clearance
    pocket_depth_xy = leg_depth + clearance
    outside_width = pocket_width + 2.0 * wall_thickness
    outside_depth = pocket_depth_xy + 2.0 * wall_thickness

    bottom_aligned = (Align.CENTER, Align.CENTER, Align.MIN)
    outside = Box(outside_width, outside_depth, lift + pocket_depth, align=bottom_aligned)
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_depth_xy,
        pocket_depth + 1.0,
        align=bottom_aligned,
    )
    return outside - pocket
