from nurb import *

TOL = 1e-6


@part
def leg_cup(wall_thickness=2.0, pocket_depth=8.0, leg_clearance=0.4, chamfer_size=1.0, draft=False):
    """A cup the short bench leg drops into, whose solid floor lifts that corner level.

    wall_thickness: how thick the sides of the cup are around the leg
    pocket_depth: how far down the leg's foot sits into the cup
    leg_clearance: extra room across the pocket so the cup slips on by hand
    chamfer_size: how big the bevel is on the outside corners
    """
    if chamfer_size < 0.8:
        reject(
            f"chamfer_size {chamfer_size} is under the 0.8mm floor a chamfer prints at "
            f"before it becomes a defect: raise it to 0.8 or more",
            param="chamfer_size",
        )

    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + leg_clearance
    pocket_length = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_length = pocket_length + 2 * wall_thickness
    height = lift + pocket_depth

    body = Pos(0, 0, height / 2) * Box(outer_width, outer_length, height)
    # The cutter runs past the rim so the mouth opens on a clean plane instead of on a
    # face coincident with the top of the body.
    over = 1.0
    pocket = Pos(0, 0, lift + (pocket_depth + over) / 2) * Box(
        pocket_width, pocket_length, pocket_depth + over
    )
    cup = body - pocket
    if draft:
        return cup

    def concave(shape):
        """Concave edges by their midpoints, so a reselect after a chamfer still knows
        them: the pocket's inside corners and the joint where its floor meets its
        walls, which a cosmetic chamfer would feather rather than relieve."""
        return {tuple(round(v, 3) for v in e.center()) for e in concave_edges(shape)}

    def mouth(edge, rim):
        """The rim of the pocket, where the leg mates. No lead-in chamfer."""
        spot = edge.center()
        return (
            edge.bounding_box().min.Z >= rim - TOL
            and abs(spot.X) <= pocket_width / 2 + TOL
            and abs(spot.Y) <= pocket_length / 2 + TOL
        )

    # Two passes, because one pass over both sets caps every top corner with a 0.87mm2
    # sliver where three chamfer faces fail to meet. Cutting the vertical corners first
    # leaves the rim chamfers two edges to miter along instead of three.
    bed, rim = cup.bounding_box().min.Z, cup.bounding_box().max.Z
    inside = concave(cup)

    def corner(edge):
        span = edge.bounding_box()
        if tuple(round(v, 3) for v in edge.center()) in inside:
            return False
        return span.min.Z <= bed + TOL and span.max.Z >= rim - TOL

    cup = polish(cup, cup.edges().filter_by(Axis.Z).filter_by(corner), chamfer_size)

    rim = cup.bounding_box().max.Z
    inside = concave(cup)

    def crest(edge):
        if tuple(round(v, 3) for v in edge.center()) in inside:
            return False
        return edge.bounding_box().min.Z >= rim - TOL and not mouth(edge, rim)

    return polish(cup, cup.edges().filter_by(crest), chamfer_size)
