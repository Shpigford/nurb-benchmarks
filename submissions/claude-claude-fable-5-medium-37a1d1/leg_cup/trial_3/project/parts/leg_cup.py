from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, draft=False):
    """Slip-over foot cup for the short leg of a wobbly bench.

    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far the leg's foot drops into the cup
    leg_clearance: total extra width in the pocket so the leg slides in
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    inner_w = leg_width + leg_clearance
    inner_d = leg_depth + leg_clearance
    outer_w = inner_w + 2 * wall_thickness
    outer_d = inner_d + 2 * wall_thickness
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height)
    bed = body.bounding_box().min.Z
    pocket = Pos(0, 0, bed + lift + pocket_depth / 2) * Box(inner_w, inner_d, pocket_depth)
    body = body - pocket
    if draft:
        return body
    # Keep the bed edges and the pocket (a mating fit) sharp; chamfer the outside only.
    def outside(e):
        bb = e.bounding_box()
        inside = abs(bb.min.X) <= inner_w / 2 + 1e-3 and abs(bb.max.X) <= inner_w / 2 + 1e-3 \
            and abs(bb.min.Y) <= inner_d / 2 + 1e-3 and abs(bb.max.Y) <= inner_d / 2 + 1e-3
        return bb.min.Z > bed and not inside
    keep = body.edges().filter_by(outside)
    return polish(body, keep, 1.0)
