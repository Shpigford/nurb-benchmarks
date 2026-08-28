from math import cos, radians, sin, sqrt

from nurb import *

# The bench interface. Several identical rests stand in a row and one pole lies across
# all of them, so every rest has to put the axis at the same height: this is a fact
# about the row, not a dimension anyone gets to drag.
AXIS_HEIGHT = 18.0

# What has to stay between the bottom of the cradle and the bed, so the seat is not
# standing on a skin.
MIN_FLOOR = 2.0

# The rest is set down on a bench and a wet pole is lowered onto it. Less footprint
# than this and it skates instead of standing.
MIN_BED_CONTACT = 230.0

# One size on every polished edge. Three chamfers meeting at a square corner leave an
# equilateral triangle of 0.866 * size ** 2, so 1mm leaves 0.87mm2 facets on all four top
# corners: real slivers, under the 1mm floor. 1.2mm puts them at 1.25mm2 and the part
# carries no sub-millimetre faces at all.
CHAMFER = 1.2


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_clearance=0.25,
    cradle_wrap=134.0,
    cradle_thickness=2.5,
    rest_length=30.0,
    waist=4.0,
    foot_height=4.0,
    draft=False,
):
    """A saddle that cradles a freshly finished pole off the bench while it dries.

    pole_diameter: how thick the pole is
    pole_clearance: the gap left between the pole and the cradle it lies in
    cradle_wrap: how far the cradle curves up around the pole, in degrees
    cradle_thickness: how much material sits behind the cradle where it is thinnest
    rest_length: how much of the pole's length this one rest sits under
    waist: how far each side is drawn in at the foot
    foot_height: how tall the straight foot is before the sides flare out
    """
    cradle_radius = pole_diameter / 2.0 + pole_clearance

    if not 0.1 <= pole_clearance <= 0.4:
        reject(
            f"pole_clearance {pole_clearance} is outside the 0.1 to 0.4 window: under 0.1 "
            "the cradle rubs the wet finish, over 0.4 the pole balances on the rim "
            "instead of lying in the seat",
            param="pole_clearance",
        )
    if not 120.0 <= cradle_wrap <= 180.0:
        reject(
            f"cradle_wrap {cradle_wrap} is outside 120 to 180 degrees: under 120 the pole "
            "sits on two edges rather than in a cradle, over 180 the rim closes over it "
            "and it can no longer be lowered straight in",
            param="cradle_wrap",
        )
    if cradle_thickness < 2.0:
        reject(
            f"cradle_thickness {cradle_thickness} is under the 2mm minimum wall: raise it "
            "to 2.0 or more",
            param="cradle_thickness",
        )
    if rest_length < 20.0:
        reject(
            f"rest_length {rest_length} bears on too little of the pole to hold it steady: "
            "raise it to 20.0 or more",
            param="rest_length",
        )
    floor = AXIS_HEIGHT - cradle_radius
    if floor < MIN_FLOOR:
        widest = 2.0 * (AXIS_HEIGHT - MIN_FLOOR - pole_clearance)
        reject(
            f"pole_diameter {pole_diameter} leaves {floor:.2f}mm of floor under the cradle "
            f"at the bench's {AXIS_HEIGHT:.1f}mm axis height: the widest pole this row of "
            f"rests can carry is {widest:.1f}",
            param="pole_diameter",
        )

    # The cradle is an arc of `cradle_wrap` centred on the bottom of the pole, so the top
    # face of the rest is wherever that arc runs out.
    half_wrap = radians(cradle_wrap / 2.0)
    rim_x = cradle_radius * sin(half_wrap)
    top_z = AXIS_HEIGHT - cradle_radius * cos(half_wrap)

    # The shoulder stands where a vertical wall leaves exactly `cradle_thickness` of
    # material behind the rim, which is the thinnest point of the whole arc.
    side = (cradle_radius + cradle_thickness) * sin(half_wrap)

    # The waist is a 45 degree flare, and the line it lies on must stay outside the
    # cradle's backing circle or it eats the wall it is supposed to be behind. That line
    # is x - z = foot_half - foot_height, and it clears the circle when that constant
    # stays above `flank_limit`.
    flank_limit = sqrt(2.0) * (cradle_radius + cradle_thickness) - AXIS_HEIGHT
    foot_height = min(foot_height, max(1.0, top_z - waist - 1.5))
    foot_half = max(side - waist, MIN_BED_CONTACT / (2.0 * rest_length), flank_limit + foot_height)
    foot_half = min(foot_half, side)
    flare = side - foot_half

    if flare < 0.05:
        outline = [(-side, 0.0), (side, 0.0), (side, top_z), (-side, top_z)]
    else:
        outline = [
            (-foot_half, 0.0),
            (foot_half, 0.0),
            (foot_half, foot_height),
            (side, foot_height + flare),
            (side, top_z),
            (-side, top_z),
            (-side, foot_height + flare),
            (-foot_half, foot_height),
        ]

    blank = extrude(Plane.XZ * Polygon(*outline, align=None), amount=rest_length / 2.0, both=True)

    # One cylinder along Y at the bench's axis height. Nothing of the rest reaches above
    # `top_z`, and `top_z` is below the axis, so the pole lowers straight in.
    seat = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(cradle_radius, rest_length + 4.0)
    body = blank - seat

    if draft:
        return body

    # The seat is the mating surface and its rim is where the wrap runs out, so every edge
    # the cut made stays sharp: a lead-in chamfer there is arc the pole no longer rests on.
    # Concave edges are never polished, and neither is anything lying in the bed face,
    # though a vertical corner that merely ends there keeps its chamfer.
    bed = body.bounding_box().min.Z
    skip = {_key(e) for e in new_edges(blank, seat, combined=body)}
    skip |= {_key(e) for e in concave_edges(body)}
    keep = body.edges().filter_by(
        lambda e: _key(e) not in skip and e.bounding_box().max.Z > bed + 1e-6
    )
    return polish(body, keep, CHAMFER)


def _key(edge):
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4), round(edge.length, 4))
