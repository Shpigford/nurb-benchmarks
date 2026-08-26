from math import radians, sin, cos

from nurb import *

AXIS_HEIGHT = 18.0
POLE_CLEARANCE = 0.25


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    rest_length=30.0,
    wrap_degrees=130.0,
    wall=3.0,
    draft=False,
):
    """
    pole_diameter: diameter of the pole this rest cradles
    rest_length: how long the rest is along the pole
    wrap_degrees: how far around the pole's circumference the cradle wraps
    wall: minimum material behind the cradle surface, backing the pole's weight
    """
    if pole_diameter <= 0:
        reject(f"pole_diameter {pole_diameter} is not a size: it must be positive", param="pole_diameter")
    if wrap_degrees < 120.0:
        reject(f"wrap_degrees {wrap_degrees} is under the 120 degree minimum a cradle needs to hold the pole without balancing on an edge: raise it to at least 120", param="wrap_degrees")
    if wrap_degrees >= 180.0:
        reject(f"wrap_degrees {wrap_degrees} wraps past the pole's midline: the pole could no longer drop in from above, raise it below 180", param="wrap_degrees")
    if rest_length < 20.0:
        reject(f"rest_length {rest_length} is under the 20mm minimum this rest needs along the pole", param="rest_length")

    pole_radius = pole_diameter / 2.0
    seat_radius = pole_radius + POLE_CLEARANCE
    half_wrap = radians(wrap_degrees / 2.0)

    if AXIS_HEIGHT - seat_radius < 2.0:
        reject(f"pole_diameter {pole_diameter} leaves under 2mm of material below the seat at axis height {AXIS_HEIGHT}: shrink the pole or raise the mount", param="pole_diameter")

    shoulder_top = AXIS_HEIGHT - seat_radius * cos(half_wrap)
    open_half_width = seat_radius * sin(half_wrap)
    half_width = open_half_width + wall

    blank = Box(
        2 * half_width,
        rest_length,
        shoulder_top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = (
        Pos(0, 0, AXIS_HEIGHT)
        * Rot(X=90)
        * Cylinder(
            seat_radius,
            rest_length * 2,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
    )
    body = blank - seat

    if draft:
        return body

    # The seat's rim is the mating surface the pole beds into: never polish it.
    mating = new_edges(blank, seat, combined=body)
    concave = concave_edges(body)
    bed = body.bounding_box().min.Z
    # The shoulder's outer top edge backs the seat right up to its rim; chamfering
    # it along the whole cradle thins that backing, so it stays sharp too.
    shoulder_rim = body.edges().filter_by(
        lambda e: abs(abs(e.position_at(0.5).X) - half_width) < 1e-4
        and abs(e.position_at(0.5).Z - shoulder_top) < 1e-4
    )
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed
        and e not in concave
        and e not in mating
        and e not in shoulder_rim
    )
    return polish(body, keep, 1.0)
