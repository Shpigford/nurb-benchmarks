from nurb import *


@part
def leg_cup(
    leg_width=measured("leg_width"),
    leg_depth=measured("leg_depth"),
    lift=measured("lift"),
    leg_clearance=0.4,
    wall_thickness=2.0,
    pocket_depth=8.0,
    draft=False,
):
    """A slip-over foot cup: the bench leg drops in from above and the solid floor
    under it lifts that corner until the bench stops rocking.

    leg_width: the wide side of the bench leg, across the flats
    leg_depth: the narrow side of the bench leg
    lift: how far the cup raises this leg off the floor
    leg_clearance: how much wider than the leg the pocket is, so it slips on by hand
    wall_thickness: how thick the wall around the leg is, on all four sides
    pocket_depth: how far the leg drops into the cup before it lands on the floor
    """
    pocket_x = leg_width + leg_clearance
    pocket_y = leg_depth + leg_clearance
    outer_x = pocket_x + 2 * wall_thickness
    outer_y = pocket_y + 2 * wall_thickness
    height = lift + pocket_depth

    # Cut the pocket from above rather than shelling, so its floor stays one flat face
    # and the walls stay exactly `wall_thickness` the whole way up to the rim. The
    # cutter runs past the top instead of landing flush on it, which is a coincident
    # face the boolean does not have to think about.
    over = 1.0
    body = Pos(0, 0, height / 2) * Box(outer_x, outer_y, height)
    mouth = Pos(0, 0, height + over - (pocket_depth + over) / 2) * Box(
        pocket_x, pocket_y, pocket_depth + over
    )
    body = body - mouth
    if draft:
        return body

    # Polish the four outside corners and nothing else. The pocket is the mating mouth
    # the leg slides into, its inside corners are concave, the bottom rim lies in the
    # bed face, and the top rim is 2mm of flat with that mating mouth on its other
    # side, which is less face than a 1mm chamfer wants beside geometry it may not
    # touch. The vertical corners are what a foot and a hand actually meet.
    bed = body.bounding_box().min.Z
    inside = concave_edges(body)
    keep = []
    for edge in body.edges():
        box = edge.bounding_box()
        in_pocket = (
            box.min.X >= -pocket_x / 2 - 1e-6
            and box.max.X <= pocket_x / 2 + 1e-6
            and box.min.Y >= -pocket_y / 2 - 1e-6
            and box.max.Y <= pocket_y / 2 + 1e-6
        )
        on_bed = box.max.Z <= bed + 1e-6
        at_rim = box.min.Z >= height - 1e-6
        if in_pocket or on_bed or at_rim or any(edge == c for c in inside):
            continue
        keep.append(edge)
    return polish(body, keep, 1.0)
