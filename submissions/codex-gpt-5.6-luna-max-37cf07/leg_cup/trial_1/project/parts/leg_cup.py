from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup for the measured rectangular workbench leg.

    leg_width and leg_depth: measured outside dimensions of the leg.
    lift: provisional floor lift that raises the bench above the floor.
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    wall = 2.0
    clearance = 0.4
    pocket_depth = 8.0
    pocket_width = leg_width + clearance
    pocket_depth_xy = leg_depth + clearance
    outer_width = pocket_width + 2.0 * wall
    outer_depth = pocket_depth_xy + 2.0 * wall
    outer_height = lift + pocket_depth

    # Box is centred by default; place both solids so the bed is z=0 and the
    # pocket floor is exactly lift above it.  Its top coincides with the rim.
    body = Pos(outer_width / 2.0, outer_depth / 2.0, outer_height / 2.0) * Box(
        outer_width, outer_depth, outer_height
    )
    pocket = Pos(
        wall + pocket_width / 2.0,
        wall + pocket_depth_xy / 2.0,
        lift + pocket_depth / 2.0,
    ) * Box(pocket_width, pocket_depth_xy, pocket_depth)
    body = body - pocket

    if draft:
        return body

    # This is a fit-critical pocket, so leave all mating and rim edges square.
    # The exposed outside top edges are also the rim boundary and must remain
    # exact to preserve the stated 26.4 x 22.9 x (lift + 8.0) envelope.
    return body
