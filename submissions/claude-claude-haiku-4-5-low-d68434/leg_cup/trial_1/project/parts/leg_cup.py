from nurb import *

@part
def leg_cup(lift=3.5):
    """Slip-over foot cup to level a wobbly workbench.

    lift: solid floor height that lifts the bench (mm)
    """
    # Read measurements from measurements.toml
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    # Pocket dimensions: leg size plus 0.4 mm clearance on each side
    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    pocket_height = 8.0

    # Wall and floor dimensions
    wall_thickness = 2.0

    # Outer dimensions of the cup base
    outer_width = pocket_width + 2 * wall_thickness
    outer_depth = pocket_depth + 2 * wall_thickness
    total_height = lift + pocket_height

    # Create the solid base block, centered at origin then translated up
    # so the bottom sits at z=0
    base = Box(outer_width, outer_depth, total_height)
    base = base.translate((0, 0, total_height / 2))

    # Create the pocket cavity (8mm deep, positioned at the top)
    # Centered horizontally, positioned with top at z = total_height
    pocket = Box(pocket_width, pocket_depth, pocket_height)
    pocket = pocket.translate((0, 0, lift + pocket_height / 2))

    # Subtract the pocket from the base
    cup = base - pocket

    return cup
