from nurb import *


@part
def leg_cup(draft=False):
    """Slip-over cup that lifts a short workbench leg level.

    The pocket, walls, and floor all track measurements.toml: leg_width,
    leg_depth, and lift. Clearance, wall thickness, and pocket depth are
    fixed by the print.

    clearance: extra space around the leg in the pocket (0.4 mm)
    wall: wall thickness on all four sides (2.0 mm)
    pocket_depth: how far the leg drops into the cup (8.0 mm)
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    clearance = 0.4
    wall = 2.0
    pocket_depth = 8.0

    pocket_w = leg_width + clearance
    pocket_d = leg_depth + clearance
    outer_w = pocket_w + 2 * wall
    outer_d = pocket_d + 2 * wall
    height = lift + pocket_depth

    body = Box(outer_w, outer_d, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Cutter stands on the floor of the pocket and overruns the rim so the
    # kernel cannot leave a coincident cap on the opening.
    cutter = Pos(0, 0, lift) * Box(
        pocket_w,
        pocket_d,
        pocket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cup = body - cutter

    if draft:
        return cup

    bed = cup.bounding_box().min.Z
    # Pocket walls stay square: inner size is a fit, and a 1 mm chamfer on
    # both rims of a 2 mm wall would knife the top. Polish the outer edges
    # that sit above the bed.
    def keep_edge(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 1e-4:
            return False
        c = e.center()
        inside = abs(c.X) < pocket_w / 2 + 0.05 and abs(c.Y) < pocket_d / 2 + 0.05
        return not inside

    keep = cup.edges().filter_by(keep_edge)
    return polish(cup, keep, 1.0)
