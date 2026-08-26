from nurb import *


@part
def leg_cup(leg_clearance=0.4, wall_thickness=2.0, pocket_depth=8.0, draft=False):
    """Slip-over foot cup that levels a wobbly bench leg.

    leg_clearance: extra pocket width so the leg drops in by hand
    wall_thickness: how thick the cup's four walls are
    pocket_depth: how deep the leg sits inside the cup
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_w = leg_width + leg_clearance
    pocket_d = leg_depth + leg_clearance
    outer_w = pocket_w + 2 * wall_thickness
    outer_d = pocket_d + 2 * wall_thickness
    outer_h = lift + pocket_depth

    body = Box(outer_w, outer_d, outer_h)
    pocket = Box(pocket_w, pocket_d, pocket_depth)
    pocket = pocket.translate((0, 0, (outer_h - pocket_depth) / 2))
    body = body - pocket
    body = body.translate((0, 0, outer_h / 2))

    if draft:
        return body
    # Chamfer only the outer shell: vertical corners and the outer top rim.
    # The pocket mouth is fit-critical (no lead-in) and the pocket floor is concave.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > 0
        and (
            abs(abs(e.bounding_box().max.X) - outer_w / 2) < 1e-6
            or abs(abs(e.bounding_box().max.Y) - outer_d / 2) < 1e-6
        )
    )
    return polish(body, keep, 1.0)
