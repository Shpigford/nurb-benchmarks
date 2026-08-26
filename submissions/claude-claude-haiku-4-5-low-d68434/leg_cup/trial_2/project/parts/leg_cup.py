from build123d import *
from nurb import *

@part
def leg_cup():
    """Slip-over foot cup to level a wobbly workbench."""
    # Read measurements
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    # Pocket dimensions (leg + 0.4mm clearance)
    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    pocket_height = 8.0

    # Outer dimensions (pocket + 2mm walls on each side)
    outer_width = pocket_width + 4.0
    outer_depth = pocket_depth + 4.0
    total_height = lift + pocket_height

    # Create base solid
    base = Box(outer_width, outer_depth, total_height)

    # Create pocket opening
    pocket = Box(pocket_width, pocket_depth, pocket_height)

    # Position pocket:
    # - Base is centered at origin, so bottom is at z = -total_height/2 = -(lift + pocket_height)/2
    # - Pocket bottom should be at z = -total_height/2 + lift
    # - Pocket center is at z = -total_height/2 + lift + pocket_height/2
    base_bottom_z = -total_height / 2
    pocket_bottom_z = base_bottom_z + lift
    pocket_center_z = pocket_bottom_z + pocket_height / 2

    pocket_pos = Vector(
        (outer_width - pocket_width) / 2,
        (outer_depth - pocket_depth) / 2,
        pocket_center_z,
    )
    pocket = pocket.locate(Location(pocket_pos))

    # Remove pocket from base
    cup = base - pocket

    return cup
