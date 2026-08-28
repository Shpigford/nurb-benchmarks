from nurb import *


@part
def leg_cup(draft=False):
    """A slip-over leveling cup for the workbench's short rectangular leg."""
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0
    pocket_width = leg_width + clearance
    pocket_length = leg_depth + clearance

    outer = Box(
        pocket_width + 2.0 * wall_thickness,
        pocket_length + 2.0 * wall_thickness,
        lift + pocket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Let the cutter just clear the top face, leaving an open, exactly 8 mm deep pocket.
    pocket = Pos(0, 0, lift) * Box(
        pocket_width,
        pocket_length,
        pocket_depth + 0.01,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return outer - pocket
