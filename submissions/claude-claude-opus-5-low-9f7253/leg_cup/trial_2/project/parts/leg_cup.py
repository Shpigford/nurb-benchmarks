from nurb import *

LEG_WIDTH = measured("leg_width")
LEG_DEPTH = measured("leg_depth")
LIFT = measured("lift")


@part
def leg_cup(
    fit_gap=0.4,
    wall_thickness=2.0,
    pocket_depth=8.0,
    lift=LIFT,
    draft=False,
):
    """A cup the wobbly leg's foot drops into, lifting the bench level.

    fit_gap: extra room around the leg so the foot slides into the pocket
    wall_thickness: how thick the four walls around the foot are
    pocket_depth: how far the foot drops into the cup
    lift: how much the solid floor raises that corner of the bench
    """
    pocket_x = LEG_WIDTH + fit_gap
    pocket_y = LEG_DEPTH + fit_gap
    outer_x = pocket_x + 2 * wall_thickness
    outer_y = pocket_y + 2 * wall_thickness
    height = lift + pocket_depth

    body = Box(outer_x, outer_y, height)
    pocket = Pos(0, 0, -height / 2 + lift + pocket_depth / 2) * Box(pocket_x, pocket_y, pocket_depth)
    body = body - pocket

    if draft:
        return body

    # Only the outer shell gets chamfered: the pocket must stay exactly on size.
    half_x, half_y = outer_x / 2, outer_y / 2
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and (
            abs(abs(e.bounding_box().center().X) - half_x) < 1e-6
            or abs(abs(e.bounding_box().center().Y) - half_y) < 1e-6
        )
    )
    return polish(body, keep, 1.0)
