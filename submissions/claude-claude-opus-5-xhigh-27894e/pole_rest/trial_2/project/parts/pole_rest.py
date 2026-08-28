from nurb import *

# The bench interface, fixed for the whole row of rests: every one of them holds the
# pole's axis at this height, so the pole lies level across all of them.
AXIS_HEIGHT = 18.0

# Radial gap between the cradle and the pole. Wet finish wants to be cradled rather
# than gripped, so this is a drop-in gap, not a fit: big enough that the pole never
# binds on the way down, small enough that the cradle still carries it as an arc.
POLE_CLEARANCE = 0.25

# The corbel: a short vertical tip at the bed, then a 45 degree plane out to the
# cradle's full width. The doctrine's corbel numbers, not a free choice.
FOOT_HEIGHT = 4.0
FOOT_RATIO = 0.6
MIN_FOOT_HALF = 5.0

# One chamfer size everywhere. 1.2 rather than 1.0 because three of them meet at each
# top corner, and 0.866 * 1.2 ** 2 puts that corner triangle over the 1mm2 sliver floor
# instead of a tenth under it.
CHAMFER = 1.2


@part
def pole_rest(pole_diameter=measured("pole_diameter"), rest_length=24.0,
              cradle_thickness=3.5, draft=False):
    """A cradle that holds a freshly finished pole clear of the bench while it dries.

    pole_diameter: how thick the pole is, measured across
    rest_length: how much of the pole's length this one rest supports
    cradle_thickness: how much material wraps around the outside of the cradle
    """
    pole_radius = pole_diameter / 2.0
    groove_radius = pole_radius + POLE_CLEARANCE
    floor = AXIS_HEIGHT - groove_radius
    if floor < 3.0:
        reject(
            f"pole_diameter {pole_diameter:g} leaves {floor:.1f}mm of floor under the "
            f"cradle at the fixed {AXIS_HEIGHT:g}mm axis height: keep it under "
            f"{2 * (AXIS_HEIGHT - 3.0 - POLE_CLEARANCE):g}",
            param="pole_diameter",
        )

    outer_half = groove_radius + cradle_thickness
    foot_half = max(outer_half * FOOT_RATIO, MIN_FOOT_HALF)
    flare = outer_half - foot_half
    if flare < 1.0:
        reject(
            f"pole_diameter {pole_diameter:g} makes the cradle narrower than its own "
            f"{2 * MIN_FOOT_HALF:g}mm foot: raise it above "
            f"{2 * (MIN_FOOT_HALF + 1.0 - cradle_thickness - POLE_CLEARANCE):g}",
            param="pole_diameter",
        )
    flare_top = FOOT_HEIGHT + flare

    # The corbel is a 45 degree plane, so the wall it leaves against the cradle is the
    # plane's distance from the pole axis less the cradle radius. Checked rather than
    # assumed: it is the thinnest section on the part and it moves with every parameter.
    corbel_wall = (AXIS_HEIGHT + outer_half - flare_top) / 2.0 ** 0.5 - groove_radius
    if corbel_wall < 2.5:
        reject(
            f"the corbel would pass {corbel_wall:.1f}mm from the cradle, under the "
            f"2.5mm minimum: raise cradle_thickness above "
            f"{cradle_thickness + 2.5 - corbel_wall:.1f}",
            param="cradle_thickness",
        )
    if flare_top > AXIS_HEIGHT - 2.0:
        reject(
            f"the corbel tops out at {flare_top:.1f}mm, leaving no straight wall under "
            f"the {AXIS_HEIGHT:g}mm rim: raise cradle_thickness",
            param="cradle_thickness",
        )
    if rest_length < AXIS_HEIGHT:
        reject(
            f"rest_length {rest_length:g} is shorter than the rest is tall "
            f"({AXIS_HEIGHT:g}mm), so it rocks along the pole: raise it above "
            f"{AXIS_HEIGHT:g}",
            param="rest_length",
        )

    profile = Polygon(
        (-foot_half, 0.0),
        (foot_half, 0.0),
        (foot_half, FOOT_HEIGHT),
        (outer_half, flare_top),
        (outer_half, AXIS_HEIGHT),
        (-outer_half, AXIS_HEIGHT),
        (-outer_half, flare_top),
        (-foot_half, FOOT_HEIGHT),
        align=None,
    )
    body = extrude(Plane.XZ * profile, amount=rest_length / 2.0, both=True)

    # The cradle. Its equator lands exactly on the top face, so the seat is a true half
    # circle: nothing anywhere on the part reaches inboard of the pole's widest point,
    # which is what lets the pole come straight down into it.
    cradle = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(
        groove_radius, rest_length + 4.0
    )
    body = body - cradle
    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = {_edge_key(e) for e in concave_edges(body)}
    keep = [
        e
        for e in body.edges()
        if e.bounding_box().min.Z > bed + 1e-6
        and _edge_key(e) not in concave
        and not _on_cradle(e, groove_radius)
    ]
    return polish(body, keep, CHAMFER)


def _edge_key(edge):
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4), round(edge.length, 4))


def _on_cradle(edge, groove_radius):
    """True for the seat's own edges. The cradle is mating geometry: polish stays off."""
    for t in (0.0, 0.5, 1.0):
        p = edge.position_at(t)
        r = (p.X ** 2 + (p.Z - AXIS_HEIGHT) ** 2) ** 0.5
        if abs(r - groove_radius) > 0.01:
            return False
    return True
