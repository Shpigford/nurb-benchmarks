from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup for a short rectangular workbench leg.

    Sits on the floor with the pocket open up so the foot drops in from
    above. The solid floor under the pocket is lift thick and is what
    levels the bench. Wall thickness, pocket depth, and slip clearance
    are fixed by the print; leg size and lift come from measurements.
    """
    wall = 2.0
    slack = 0.4
    pocket_depth = 8.0
    pocket_w = measured("leg_width") + slack
    pocket_d = measured("leg_depth") + slack
    lift = measured("lift")
    height = lift + pocket_depth

    body = extrude(Rectangle(pocket_w + 2 * wall, pocket_d + 2 * wall), amount=height)
    pocket = extrude(Rectangle(pocket_w, pocket_d), amount=pocket_depth + 1)
    cup = body - pocket.move(Location((0, 0, lift)))
    if draft:
        return cup
    return cup
