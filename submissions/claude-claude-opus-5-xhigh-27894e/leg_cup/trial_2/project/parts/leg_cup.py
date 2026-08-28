from nurb import *


@part
def leg_cup(foot_clearance=0.4, wall_thickness=2.0, pocket_depth=8.0, draft=False):
    """A cup the wobbly bench's short leg drops into, lifting that corner level.

    foot_clearance: extra room around the leg so the foot slips in without forcing
    wall_thickness: how thick the four sides of the cup are
    pocket_depth: how far down into the cup the leg's foot sits
    """
    # The lift is the whole point of the part, so it comes off the measurement file
    # rather than out of the signature: correct the number there and this tracks it.
    lift = measured("lift")
    pocket_width = measured("leg_width") + foot_clearance   # across the leg
    pocket_across = measured("leg_depth") + foot_clearance  # along the leg

    outer_width = pocket_width + 2 * wall_thickness
    outer_across = pocket_across + 2 * wall_thickness
    rim = lift + pocket_depth

    up = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(outer_width, outer_across, rim, align=up)
    # Overshoot the cutter past the rim so the boolean never has to resolve two
    # coplanar top faces. The pocket is still exactly pocket_depth deep, floored by
    # the solid lift underneath it.
    body -= Pos(0, 0, lift) * Box(
        pocket_width, pocket_across, pocket_depth + 1.0, align=up
    )

    if draft:
        return body

    def on_top(edge):
        box = edge.bounding_box()
        return abs(box.min.Z - rim) < 1e-6 and abs(box.max.Z - rim) < 1e-6

    def outer_corners(shape):
        """The four upright corners, the only edges running bed to rim."""
        return [
            e
            for e in shape.edges()
            if abs(e.bounding_box().min.Z) < 1e-6
            and abs(e.bounding_box().max.Z - rim) < 1e-6
        ]

    def top_ring(shape):
        """The rim's outer boundary. The pocket mouth is the only other thing up
        there, and it is the one edge that must stay square: a lead-in would eat the
        top millimetre of pocket depth and thin the wall the foot bears against."""
        out = []
        for e in shape.edges():
            middle = e.center()
            mouth = (
                abs(middle.X) <= pocket_width / 2 + 1e-6
                and abs(middle.Y) <= pocket_across / 2 + 1e-6
            )
            if on_top(e) and not mouth:
                out.append(e)
        return out

    # Two passes, because one is what leaves a sliver. Chamfering the uprights and the
    # rim together puts three chamfers on each top corner and the triangle they leave
    # is 0.87mm2, under the sliver floor. Taking the uprights first gives that corner a
    # real edge to miter along, so the rim pass reselects eight edges instead of four
    # and every one of them lands.
    body = polish(body, outer_corners(body), 1.0)
    body = polish(body, top_ring(body), 1.0)

    # Nothing else is chamfered on purpose: the bed edges stay square so the cup keeps
    # its full first layer under load, and the pocket's floor perimeter and inside
    # corners are concave, where a cosmetic chamfer is a feather edge rather than a
    # corner taken off.
    return body
