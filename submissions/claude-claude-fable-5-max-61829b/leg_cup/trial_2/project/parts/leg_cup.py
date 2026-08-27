from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, draft=False):
    """Slip-over foot cup that lifts the short leg of the workbench.

    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far the foot of the leg sinks into the cup
    leg_clearance: total extra room in the pocket over the measured leg, so it drops in
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")
    if lift <= 0:
        reject(f"lift {lift} leaves no floor under the foot: it has to be above 0")

    inner_width = leg_width + leg_clearance
    inner_depth = leg_depth + leg_clearance
    outer_width = inner_width + 2 * wall_thickness
    outer_depth = inner_depth + 2 * wall_thickness

    on_bed = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(outer_width, outer_depth, lift + pocket_depth, align=on_bed)
    # The cutter overshoots the rim so the cut never leaves a coplanar skin.
    pocket = Pos(0, 0, lift) * Box(inner_width, inner_depth, pocket_depth + 1.0, align=on_bed)
    cup = body - pocket
    if draft:
        return cup

    # Polish the vertical corners and the outer rim only. The bottom edges lie in the
    # bed face, and the pocket is the fit, so its mouth, corners and floor stay sharp.
    def outside_pocket(edge):
        c = edge.center()
        return abs(c.X) > inner_width / 2 + 1e-6 or abs(c.Y) > inner_depth / 2 + 1e-6

    # Corners first, then the rim across them: chamfering all eight edges in one pass
    # leaves a 0.87mm2 triangle at each top corner, which is a sliver by the rules.
    corners = cup.edges().filter_by(Axis.Z).filter_by(outside_pocket)
    cornered = polish(cup, corners, 1.0)
    rim = cornered.edges().group_by(Axis.Z)[-1].filter_by(outside_pocket)
    return polish(cornered, rim, 1.0)
