from nurb import *


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, draft=False):
    """Slip-over foot cup that lifts the short leg of a wobbly workbench.

    wall_thickness: how thick the four walls around the leg are
    pocket_depth: how far the leg's foot drops into the cup
    leg_clearance: total extra room in the pocket over the measured leg, so it drops in
    """
    # Every fit dimension comes from measurements.toml, read at build time so an
    # edit there (a real reading of `lift` at the shop) rebuilds the geometry.
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + leg_clearance
    pocket_length = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_length = pocket_length + 2 * wall_thickness
    height = lift + pocket_depth

    up = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(outer_width, outer_length, height, align=up)
    # The cutter overshoots the rim by 1mm so the pocket's open top is a clean cut
    # rather than two coplanar faces fighting in the boolean.
    pocket = Pos(0, 0, lift) * Box(pocket_width, pocket_length, pocket_depth + 1.0, align=up)
    cup = body - pocket
    if draft:
        return cup

    # Polish only the outside. The pocket is a socket, so its mouth and its concave
    # floor edges stay sharp; edges lying in the bed face are never chamfered.
    eps = 1e-6
    top = cup.bounding_box().max.Z

    def on_outer_wall(edge):
        c = edge.center()
        return abs(abs(c.X) - outer_width / 2) < eps or abs(abs(c.Y) - outer_length / 2) < eps

    def on_outer_rim(edge):
        c = edge.center()
        in_top_plane = edge.bounding_box().min.Z > top - eps
        over_pocket = abs(c.X) <= pocket_width / 2 + eps and abs(c.Y) <= pocket_length / 2 + eps
        return in_top_plane and not over_pocket

    # Two passes on purpose: corners first, then the rim reselected on the result, so
    # the top bevel runs around each corner facet as one band. Chamfering all eight
    # edges at once leaves a 0.87mm2 triangle at every corner, which is a sliver.
    corners = cup.edges().filter_by(Axis.Z).filter_by(on_outer_wall)
    cornered = polish(cup, corners, 1.0)
    rim = cornered.edges().filter_by(on_outer_rim)
    return polish(cornered, rim, 1.0)
