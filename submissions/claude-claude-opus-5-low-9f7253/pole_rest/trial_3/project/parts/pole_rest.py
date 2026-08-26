from nurb import *

import math

AXIS_HEIGHT = 18.0  # fixed by the bench: every rest in the row seats the pole here


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_clearance=0.1,
    rest_length=22.0,
    cradle_wall=2.6,
    seat_lip=1.2,
    draft=False,
):
    """A drying rest: the pole lies in the cradle, several rests in a row.

    pole_diameter: how thick the pole is across
    pole_clearance: the gap left between the pole's finish and the cradle
    rest_length: how far the rest runs along the pole
    cradle_wall: how much material backs the cradle behind the pole
    seat_lip: how far the cradle walls rise past the pole's widest cradled point
    """
    seat_radius = pole_diameter / 2.0 + pole_clearance
    if seat_radius >= AXIS_HEIGHT - 2.0:
        reject(
            f"pole_diameter {pole_diameter} leaves under 2mm of floor beneath the seat "
            f"at the fixed {AXIS_HEIGHT}mm axis height: lower it below {2 * (AXIS_HEIGHT - 2.0 - pole_clearance)}",
            param="pole_diameter",
        )

    # Cradle the pole over 126 degrees: the walls rise to 63 degrees off the bottom,
    # which keeps the mouth wider than the pole the whole way down (it drops straight in).
    top = AXIS_HEIGHT - seat_radius * math.cos(math.radians(63.0)) + seat_lip
    half_width = math.sqrt(max(seat_radius**2 - (AXIS_HEIGHT - top) ** 2, 0.0)) + cradle_wall

    body = Pos(0, 0, top / 2) * Box(2 * half_width, rest_length, top)
    seat = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(seat_radius, rest_length + 2)
    body = body - seat

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = concave_edges(body)
    keep = [
        e
        for e in body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 1e-6)
        if e not in concave
    ]
    return polish(body, keep, 1.0)
