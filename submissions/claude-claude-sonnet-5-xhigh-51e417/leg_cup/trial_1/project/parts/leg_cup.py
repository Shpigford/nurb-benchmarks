from nurb import *


@part
def leg_cup(wall=2.0, pocket_depth=8.0, fit=0.4, draft=False):
    """
    wall: how thick the floor and side walls of the cup are
    pocket_depth: how deep the pocket is, from its rim down to its floor
    fit: total extra room the pocket leaves around the leg, split across each side
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + fit
    pocket_length = leg_depth + fit
    outer_width = pocket_width + 2 * wall
    outer_length = pocket_length + 2 * wall
    outer_height = lift + pocket_depth

    align_floor = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(outer_width, outer_length, outer_height, align=align_floor)
    pocket = Pos(0, 0, lift) * Box(pocket_width, pocket_length, pocket_depth, align=align_floor)
    body -= pocket

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = set(concave_edges(body))
    outer_x, outer_y = outer_width / 2, outer_length / 2

    def on_outer_corner(edge):
        # Vertical outer corners only: X and Y both constant, at the outer
        # footprint. The top rim shares those same corners, and chamfering both
        # there caps each one with a sub-mm2 sliver, so the rim stays sharp.
        bb = edge.bounding_box()
        x_const = abs(bb.max.X - bb.min.X) < 1e-6 and abs(abs(bb.min.X) - outer_x) < 1e-6
        y_const = abs(bb.max.Y - bb.min.Y) < 1e-6 and abs(abs(bb.min.Y) - outer_y) < 1e-6
        return x_const and y_const

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > bed and e not in concave and on_outer_corner(e)
    )
    return polish(body, keep, 1.0)
