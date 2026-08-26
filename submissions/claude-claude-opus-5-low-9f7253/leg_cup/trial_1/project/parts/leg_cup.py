from nurb import *

LEG_WIDTH = measured("leg_width")
LEG_DEPTH = measured("leg_depth")
LIFT = measured("lift")


@part
def leg_cup(
    clearance=0.4,
    wall=2.0,
    pocket_depth=8.0,
    edge_chamfer=1.0,
    draft=False,
):
    """A slip-over cup for the bench's short leg: the foot drops in, the solid floor lifts the bench.

    clearance: how much wider the pocket is than the leg, so the foot slips in
    wall: how thick the four walls around the leg are
    pocket_depth: how far the leg's foot sits down into the cup
    edge_chamfer: how much the outside edges are broken for a clean print
    """
    pocket_w = LEG_WIDTH + clearance
    pocket_d = LEG_DEPTH + clearance
    outer_w = pocket_w + 2 * wall
    outer_d = pocket_d + 2 * wall
    height = LIFT + pocket_depth

    body = Box(outer_w, outer_d, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket = Box(
        pocket_w, pocket_d, pocket_depth, align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).translate((0, 0, LIFT))
    cup = body - pocket

    if draft:
        return cup

    bed = cup.bounding_box().min.Z
    outer_half_w = outer_w / 2
    outer_half_d = outer_d / 2

    def outside(e):
        bb = e.bounding_box()
        if bb.min.Z < bed + 1e-6 and bb.max.Z < bed + 1e-6:
            return False
        on_side = (
            bb.min.X > outer_half_w - 1e-6
            or bb.max.X < -outer_half_w + 1e-6
            or bb.min.Y > outer_half_d - 1e-6
            or bb.max.Y < -outer_half_d + 1e-6
        )
        vertical = bb.max.Z - bb.min.Z > 1e-6
        return on_side and vertical

    keep = cup.edges().filter_by(outside)
    return polish(cup, keep, edge_chamfer)
