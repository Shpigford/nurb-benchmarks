from nurb import *


@part
def leg_cup(
    wall_thickness=2.0,
    pocket_depth=8.0,
    leg_clearance=0.4,
    corner_chamfer=1.0,
    draft=False,
):
    """A slip-over foot cup that lifts the short leg of a wobbly workbench.

    wall_thickness: how thick the four side walls are around the leg
    pocket_depth: how far the leg's foot drops down into the cup
    leg_clearance: extra room across the pocket so the leg slips on by hand
    corner_chamfer: how much the four outside corners are eased off
    """
    leg_width = measured("leg_width")
    leg_depth = measured("leg_depth")
    lift = measured("lift")

    pocket_width = leg_width + leg_clearance
    pocket_length = leg_depth + leg_clearance
    outer_width = pocket_width + 2 * wall_thickness
    outer_length = pocket_length + 2 * wall_thickness
    height = lift + pocket_depth

    body = Box(outer_width, outer_length, height)
    top = height / 2

    # Cut the pocket clean out through the top face, so nothing is left roofing it
    # over. The overshoot lands outside the body and costs the shape nothing.
    overshoot = 1.0
    mouth = Pos(0, 0, top - pocket_depth + (pocket_depth + overshoot) / 2) * Box(
        pocket_width, pocket_length, pocket_depth + overshoot
    )
    cup = body - mouth

    if draft:
        return cup

    box = cup.bounding_box()
    inside = concave_edges(cup)

    def concave(edge):
        here = edge.center()
        return any((here - other.center()).length < 1e-6 for other in inside)

    # The four outside corners, and only those: they are the edges a hand meets when
    # the cup goes on. Everything else is excluded for a reason the card records --
    # the bed face stays flat, the rim keeps its full wall thickness, and the pocket
    # is the surface the leg slides into.
    corners = [
        edge
        for edge in cup.edges()
        if not concave(edge)
        and edge.bounding_box().min.Z < box.min.Z + 1e-6
        and edge.bounding_box().max.Z > box.max.Z - 1e-6
    ]
    return polish(cup, corners, corner_chamfer)
