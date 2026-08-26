from nurb import *


@part
def leg_cup(pocket_clearance=0.4, wall_thickness=2.0, pocket_depth=8.0, chamfer_size=1.0, draft=False):
    """A slip-over foot cup: the bench leg drops in and the solid floor lifts it level.

    pocket_clearance: how much wider than the leg the pocket is, total across each side
    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far the leg foot drops into the cup
    chamfer_size: how much is taken off the outer vertical corners
    """
    lift = measured("lift")
    pocket_x = measured("leg_width") + pocket_clearance
    pocket_y = measured("leg_depth") + pocket_clearance

    outer_x = pocket_x + 2 * wall_thickness
    outer_y = pocket_y + 2 * wall_thickness
    height = lift + pocket_depth

    body = Pos(0, 0, height / 2) * Box(outer_x, outer_y, height)
    pocket = Pos(0, 0, lift + pocket_depth / 2) * Box(pocket_x, pocket_y, pocket_depth)
    body = body - pocket

    if draft:
        return body

    # Only the outer vertical corners: the rim is the mating mouth and the bottom
    # is the bed face, so neither gets a chamfer.
    corners = body.edges().filter_by(Axis.Z).filter_by(
        lambda e: abs(e.center().X) > pocket_x / 2 and abs(e.center().Y) > pocket_y / 2
    )
    return polish(body, corners, chamfer_size)
