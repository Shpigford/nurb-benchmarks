from nurb import *

# Calipered off the bench, so these are facts rather than choices: a slider on them
# would only build a cup that does not fit. Read at build time, so editing
# measurements.toml is what moves the geometry.
LEG_WIDTH = measured("leg_width")
LEG_DEPTH = measured("leg_depth")


@part
def leg_cup(
    lift=measured("lift"),
    wall_thickness=2.0,
    pocket_depth=8.0,
    foot_clearance=0.4,
    draft=False,
):
    """A cup the short bench leg stands in, whose solid floor lifts that corner level.

    Prints as it sits: flat bottom on the bed, pocket opening straight up, so every
    wall is a vertical extrusion and nothing overhangs.

    lift: how far the floor under the foot raises this corner of the bench
    wall_thickness: how thick the four side walls are
    pocket_depth: how far the leg's foot drops into the cup
    foot_clearance: total slack across the pocket so the foot slides on by hand
    """
    if lift <= 0:
        reject(
            f"lift {lift} raises the bench by nothing, so the cup fixes no wobble. "
            f"Put a positive lift in measurements.toml.",
            param="lift",
        )

    pocket_x = LEG_WIDTH + foot_clearance
    pocket_y = LEG_DEPTH + foot_clearance
    outer_x = pocket_x + 2 * wall_thickness
    outer_y = pocket_y + 2 * wall_thickness
    height = lift + pocket_depth

    # Bed at z=0, pocket mouth at z=height. The cutter runs out through the top rather
    # than stopping on it: the mouth is open by construction and the boolean never has
    # to resolve two coincident faces.
    body = Pos(0, 0, height / 2) * Box(outer_x, outer_y, height)
    cutter_depth = 2 * pocket_depth
    pocket = Pos(0, 0, lift + cutter_depth / 2) * Box(pocket_x, pocket_y, cutter_depth)
    cup = body - pocket

    if draft:
        return cup

    # Three things must not be chamfered, and what is left is the four vertical corners:
    #
    #   the bed face's own edges, which would lay a knife edge into the first layer;
    #   the pocket, a socket the foot slides into, so its mouth stays square and its
    #     inside corners stay as cut (a chamfer there is a feather edge, not a corner off);
    #   the rim's outer edge, because the wall is only 2mm and has to stay 2mm all the
    #     way up. Chamfering it also puts three chamfers on each top corner, and the
    #     0.87mm2 triangle they leave at 1mm is under what the nozzle can lay.
    #
    # The vertical corners merely end at the bed rather than lying in it, so their
    # chamfer stands square to the plate and keeps its full first-layer width.
    bed = cup.bounding_box().min.Z
    rim = cup.bounding_box().max.Z
    half_x, half_y = outer_x / 2, outer_y / 2
    concave = {tuple(round(v, 4) for v in e.center()) for e in concave_edges(cup)}

    def outer_corner(edge):
        box = edge.bounding_box()
        if box.max.Z - box.min.Z < 1e-6:
            return False  # horizontal: lies in the bed face or in the rim
        if box.max.Z <= bed + 1e-6 or box.min.Z >= rim - 1e-6:
            return False
        if tuple(round(v, 4) for v in edge.center()) in concave:
            return False
        return (
            box.max.X >= half_x - 1e-6
            or box.min.X <= -half_x + 1e-6
            or box.max.Y >= half_y - 1e-6
            or box.min.Y <= -half_y + 1e-6
        )

    return polish(cup, cup.edges().filter_by(outer_corner), 1.0)
