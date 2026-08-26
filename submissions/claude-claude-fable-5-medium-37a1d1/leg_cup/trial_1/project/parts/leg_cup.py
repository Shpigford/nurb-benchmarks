from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, draft=False):
    """Slip-over cup for a short workbench leg: the foot drops in, the floor lifts it.

    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far the leg foot drops into the cup
    leg_clearance: total extra on the pocket over the measured leg, so it slides on
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_w = leg_width + leg_clearance
    pocket_d = leg_depth + leg_clearance
    outer_w = pocket_w + 2 * wall_thickness
    outer_d = pocket_d + 2 * wall_thickness
    height = lift + pocket_depth

    # Outer block seated on the bed, pocket cut straight down to a floor `lift` thick.
    body = Pos(0, 0, height / 2) * Box(outer_w, outer_d, height)
    pocket = Pos(0, 0, lift + pocket_depth / 2) * Box(pocket_w, pocket_d, pocket_depth)
    body = body - pocket
    if draft:
        return body

    # Polish the four vertical outer corners only. The rim is a 2mm wall, so a 1mm
    # chamfer on it leaves sliver corner facets, and the pocket mouth is fit geometry
    # that stays sharp anyway. Vertical corners have the full height to land on.
    keep = body.edges().filter_by(Axis.Z).filter_by(
        lambda e: abs(e.center().X) >= outer_w / 2 - 1e-6
        and abs(e.center().Y) >= outer_d / 2 - 1e-6
    )
    return polish(body, keep, 1.0)
