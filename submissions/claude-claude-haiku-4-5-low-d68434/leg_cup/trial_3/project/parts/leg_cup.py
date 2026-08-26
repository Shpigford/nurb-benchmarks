from nurb import *


@part
def leg_cup():
    """
    A slip-over foot cup that lifts a workbench leg level.

    The cup sits on the floor with a rectangular pocket opening up.
    The bench leg drops into the pocket, and the solid base lifts the leg.
    """

    # Get measurements from measurements.toml
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    # Pocket dimensions: leg clearance is 0.4mm total
    pocket_width = leg_width + 0.4
    pocket_depth = leg_depth + 0.4
    pocket_height = 8.0

    # Wall thickness
    wall = 2.0

    # Calculate outer dimensions
    outer_width = pocket_width + 2 * wall
    outer_depth = pocket_depth + 2 * wall
    total_height = lift + pocket_height

    # Create the full outer box
    cup = Box(outer_width, outer_depth, total_height)

    # Create the pocket
    pocket = Box(pocket_width, pocket_depth, pocket_height)

    # Fillet the bottom edges of the pocket (where floor meets the walls)
    # This will create smooth transitions instead of sharp internal corners
    bottom_edges = [e for e in pocket.edges() if e.bounding_box().max.Z < -pocket_height / 2 + 0.1]
    if bottom_edges:
        pocket = fillet(bottom_edges, 0.5)

    # Position the pocket
    z_offset = (total_height - pocket_height) / 2
    pocket = pocket.translate((0, 0, z_offset))

    # Subtract the pocket
    cup = cup - pocket

    # Polish exposed edges (keep the base flat)
    bed = cup.bounding_box().min.Z
    keep = cup.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.1)
    cup = polish(cup, keep, 1.0)

    return cup
