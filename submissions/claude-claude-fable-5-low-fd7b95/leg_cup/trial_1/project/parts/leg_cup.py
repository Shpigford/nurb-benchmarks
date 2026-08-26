from nurb import *


@part
def leg_cup(clearance=0.4, wall_thickness=2.0, pocket_depth=8.0, draft=False):
    """Slip-over foot cup that lifts a wobbly workbench leg level.

    clearance: total extra pocket width so the leg drops in by hand
    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far the leg's foot sits down inside the cup
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + clearance
    pocket_length = leg_depth + clearance
    height = lift + pocket_depth

    body = Pos(0, 0, height / 2) * Box(
        pocket_width + 2 * wall_thickness,
        pocket_length + 2 * wall_thickness,
        height,
    )
    pocket = Pos(0, 0, lift + pocket_depth / 2) * Box(
        pocket_width, pocket_length, pocket_depth
    )
    body = body - pocket

    if draft:
        return body
    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and e not in concave
    )
    return polish(body, keep, 1.0)
