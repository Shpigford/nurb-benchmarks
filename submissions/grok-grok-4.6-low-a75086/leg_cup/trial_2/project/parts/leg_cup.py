from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over foot cup that lifts a short workbench leg level.

    The pocket is a slip fit on the measured rectangular leg. The solid floor
    under the pocket is the lift that levels the bench.

    lift: how far the cup raises the short leg; read from measurements.toml
    """
    clearance = 0.4
    pocket_depth = 8.0
    wall = 2.0
    lift = measured("lift")
    pocket_w = measured("leg_width") + clearance
    pocket_d = measured("leg_depth") + clearance
    outer_w = pocket_w + 2.0 * wall
    outer_d = pocket_d + 2.0 * wall
    outer_h = lift + pocket_depth

    body = Box(outer_w, outer_d, outer_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket = Box(
        pocket_w,
        pocket_d,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, lift)))
    cup = body - pocket
    if draft:
        return cup
    bed = cup.bounding_box().min.Z
    keep = cup.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 1e-6)
    keep = keep - concave_edges(cup)
    return polish(cup, keep, 1.0)
