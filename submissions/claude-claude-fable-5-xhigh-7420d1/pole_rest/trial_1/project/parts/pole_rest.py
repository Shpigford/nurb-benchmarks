import math

from nurb import *

# The one number that is a fit: calipers across the sanded pole (measurements.toml).
POLE_DIAMETER = measured("pole_diameter")


@part
def pole_rest(
    pole_diameter=POLE_DIAMETER,
    pole_height=18.0,
    seat_clearance=0.2,
    cradle_wrap=150.0,
    wall=3.0,
    length=32.0,
    draft=False,
):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is; the cradle is cut to match it
    pole_height: how high the pole's centre sits above the bench, the same on every rest in the row
    seat_clearance: the gap between the pole and the cradle, so the finish never rubs
    cradle_wrap: how many degrees of the pole's circumference the cradle reaches around
    wall: how thick the cradle wall is at its thinnest, behind the pole
    length: how long the rest is along the pole
    """
    if seat_clearance < 0.1:
        reject(
            f"seat_clearance {seat_clearance} is a bind: a printed cradle needs at least "
            "0.1 of gap around the pole, and 0.2 is the snug fit it was drawn with",
            param="seat_clearance",
        )
    if not 0.0 < cradle_wrap < 180.0:
        reject(
            f"cradle_wrap {cradle_wrap} must sit between 0 and 180: past 180 the walls "
            "close over the pole and it can no longer drop in from above",
            param="cradle_wrap",
        )
    if wall < 1.2:
        reject(
            f"wall {wall} is too thin to back the cradle: keep at least 1.2 behind the pole",
            param="wall",
        )

    seat_radius = pole_diameter / 2 + seat_clearance
    floor = pole_height - seat_radius
    if floor < 2.0:
        reject(
            f"a {pole_diameter} pole with its centre {pole_height} up leaves only "
            f"{floor:.1f}mm of rest under it; the seat needs at least 2mm of floor",
            param="pole_diameter",
        )

    # Cradle: an arc concentric with the pole reaching cradle_wrap/2 each side of the
    # bottom. The rims stop exactly where the arc ends, so the pole always clears
    # them on its way straight down.
    half_wrap = math.radians(cradle_wrap / 2)
    top = pole_height - seat_radius * math.cos(half_wrap)
    mouth = seat_radius * math.sin(half_wrap)
    outer = seat_radius + wall

    # Outside: a short vertical lip at the rim, then a 45 degree corbel falling back
    # to the foot. The lip is exactly as tall as it has to be for the corbel plane
    # to stay `wall` clear of the cradle at the 45 degree point of the arc.
    lip_bottom = pole_height + outer - outer * math.sqrt(2.0)
    lip_bottom = min(lip_bottom, top)
    # The foot stands directly under the mouth, so the flanks share a plane with the
    # cradle's inner edges; a floor keeps a rest for a thin pole from going tippy.
    foot = max(mouth, 6.0)
    root = lip_bottom - (outer - foot)
    if root < 2.0:
        reject(
            f"wall {wall} pushes the corbel root to {root:.1f}mm off the bed; "
            "a thinner wall keeps the foot standing",
            param="wall",
        )

    right = [(foot, 0.0), (foot, root), (outer, lip_bottom)]
    if top - lip_bottom > 1e-6:
        right.append((outer, top))
    points = right + [(-x, z) for x, z in reversed(right)]
    profile = Plane.XZ * Polygon(*points, align=None)
    body = extrude(profile, amount=length / 2, both=True)
    seat = Pos(0, 0, pole_height) * Rot(90, 0, 0) * Cylinder(seat_radius, length + 2.0)
    body = body - seat

    if draft:
        return body

    # Polish everything but the bed edges, the corbel roots (concave), the seat
    # (the cradle is the fit, so its arc and rim edges stay exactly as cut) and the
    # corbel tip: a chamfer on that 135 degree crease is a 0.9mm facet that leaves
    # sub-mm2 compound triangles where it meets the end chamfers.
    bed = body.bounding_box().min.Z
    seat_edges = body.faces().filter_by(GeomType.CYLINDER).edges()

    def polishable(e):
        bb = e.bounding_box()
        if bb.max.Z <= bed + 1e-6:
            return False  # lies in the bed face
        if any(e.is_same(s) for s in seat_edges):
            return False
        tip = abs(bb.min.Z - lip_bottom) < 1e-6 and abs(bb.max.Z - lip_bottom) < 1e-6
        return not (tip and bb.max.Y - bb.min.Y > 1.0)

    keep = body.edges().filter_by(polishable) - concave_edges(body)
    return polish(body, keep, 1.2)
