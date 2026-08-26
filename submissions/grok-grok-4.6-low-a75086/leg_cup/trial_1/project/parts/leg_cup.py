from nurb import *

# Slip-over foot cup: rectangular pocket for a workbench leg, solid floor of `lift`.


@part
def leg_cup(draft=False):
    """Cup the short workbench leg drops into so the bench sits level.

    pocket_clearance: extra inner size around the measured leg (fixed 0.4).
    wall_thickness: all four walls (fixed 2.0).
    pocket_depth: how far the leg sits into the cup (fixed 8.0).
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_clearance = 0.4
    wall_thickness = 2.0
    pocket_depth = 8.0

    inner_w = leg_width + pocket_clearance
    inner_d = leg_depth + pocket_clearance
    outer_w = inner_w + 2.0 * wall_thickness
    outer_d = inner_d + 2.0 * wall_thickness
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height)
    body = body.moved(Location((0, 0, height / 2.0)))

    # Cut from the rim down to the lift floor; extra height so the top stays open.
    pocket = Box(inner_w, inner_d, pocket_depth + 2.0)
    pocket = pocket.moved(Location((0, 0, lift + pocket_depth / 2.0 + 1.0)))
    cup = body - pocket

    if draft:
        return cup

    bed = cup.bounding_box().min.Z
    inner_x = inner_w / 2.0 + 0.05
    inner_y = inner_d / 2.0 + 0.05

    def outer_exposed(edge):
        if edge.bounding_box().min.Z <= bed + 0.05:
            return False
        c = edge.center()
        on_pocket = abs(c.X) <= inner_x and abs(c.Y) <= inner_y
        return not on_pocket

    keep = cup.edges().filter_by(outer_exposed)
    return polish(cup, keep, 1.0)
