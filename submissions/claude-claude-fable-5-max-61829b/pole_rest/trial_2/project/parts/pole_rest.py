from math import cos, radians, sin

from nurb import *

# The bench row fixes the interface: the pole's axis runs along Y exactly this far
# above the bed, whatever the pole's diameter is.
AXIS_HEIGHT = 18.0
# Radial gap around the pole: 0.25 drops in freely on any printer and still keeps
# the seat within a bead of the finish it must not mark.
SEAT_CLEARANCE = 0.25
# The seat wraps 2 * WRAP degrees of the pole. 75 each side cradles well past the
# 120-degree minimum and still leaves the mouth wide open for a straight drop-in.
WRAP = 75.0
# Material outboard of the seat mouth at the wall tips.
TIP_WALL = 3.6


@part
def pole_rest(pole_diameter=measured("pole_diameter"), length=22.0, draft=False):
    """A cradle that holds a freshly finished pole off the bench while it dries.

    pole_diameter: how thick the pole is, straight across
    length: how far the rest runs along the pole
    """
    seat_r = pole_diameter / 2 + SEAT_CLEARANCE
    floor = AXIS_HEIGHT - seat_r
    if pole_diameter < 3.0:
        reject(
            f"pole_diameter {pole_diameter:g} is under 3mm: the seat would print as "
            "a scratch, not a cradle. Raise it to 3 or more.",
            param="pole_diameter",
        )
    if floor < 2.4:
        limit = 2 * (AXIS_HEIGHT - 2.4 - SEAT_CLEARANCE)
        reject(
            f"the bench row fixes the pole axis at {AXIS_HEIGHT:g}mm, and "
            f"pole_diameter {pole_diameter:g} leaves only {floor:.1f}mm of material "
            f"under the seat: keep it at {limit:.1f} or less.",
            param="pole_diameter",
        )
    if length < 10.0:
        reject(
            f"length {length:g} is too short to stand in the bench row: "
            "raise it to 10 or more.",
            param="length",
        )

    top_z = AXIS_HEIGHT - seat_r * cos(radians(WRAP))
    mouth = seat_r * sin(radians(WRAP))
    half_width = mouth + TIP_WALL

    section = Rectangle(2 * half_width, top_z, align=(Align.CENTER, Align.MIN))
    section -= Pos(0, AXIS_HEIGHT) * Circle(seat_r)
    body = Pos(0, length / 2, 0) * extrude(Plane.XZ * section, amount=length)

    if draft:
        return body

    bed = body.bounding_box().min.Z
    avoid = concave_edges(body)

    def wants_chamfer(edge):
        if edge.bounding_box().max.Z <= bed + 1e-6:
            return False  # lies in the bed-contact face
        for t in (0.0, 0.5, 1.0):
            p = edge.position_at(t)
            if (p.X**2 + (p.Z - AXIS_HEIGHT) ** 2) ** 0.5 <= seat_r + 0.05:
                return False  # the seat is mating geometry: no lead-in chamfers
        return True

    keep = [e for e in body.edges() if wants_chamfer(e) and e not in avoid]
    return polish(body, keep, 1.0)
