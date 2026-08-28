from math import cos, hypot, radians, sin

from nurb import *

# Every rest in the row puts the pole's axis at the same height, so this is a fact
# about the bench the row stands on rather than a dimension of one rest.
AXIS_HEIGHT = 18.0
# Three 45-degree facets meeting at a corner leave a triangle of 0.866 * size^2.
# At 1.0mm that is 0.87mm2, which reads as a sliver; 1.2mm keeps it over the floor.
CHAMFER = 1.2


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    pole_clearance=0.2,
    wrap_angle=140.0,
    wall_thickness=3.0,
    length_along_pole=24.0,
    draft=False,
):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is across
    pole_clearance: gap between the pole and the seat, so a soft finish is not wiped going in
    wrap_angle: how far around the pole the seat reaches, in degrees
    wall_thickness: how much material wraps the seat
    length_along_pole: how much of the pole's length this one rest carries
    """
    seat_radius = pole_diameter / 2 + pole_clearance

    if pole_clearance < 0.1:
        reject(
            f"pole_clearance {pole_clearance} is under 0.1: the seat binds on the pole "
            "and drags the wet finish. Raise it to 0.1 or more.",
            param="pole_clearance",
        )
    if pole_clearance > 0.4:
        reject(
            f"pole_clearance {pole_clearance} lets the pole settle below the {AXIS_HEIGHT}mm "
            "line the row shares, touching at the bottom of the seat instead of along the "
            "arc. Keep it at 0.4 or under.",
            param="pole_clearance",
        )
    if wrap_angle < 120.0:
        reject(
            f"wrap_angle {wrap_angle} is under 120 degrees: the seat stops being a cradle "
            "and becomes two edges pressing lines into the finish. Raise it above 120.",
            param="wrap_angle",
        )
    if wrap_angle > 170.0:
        reject(
            f"wrap_angle {wrap_angle} closes the horns over the pole, so lifting it out "
            "wipes both of them. Keep it at 170 or under.",
            param="wrap_angle",
        )
    if wall_thickness < 2.0:
        reject(
            f"wall_thickness {wall_thickness} is under the 2mm printable minimum for a "
            "wall carrying load. Raise it to 2.0 or more.",
            param="wall_thickness",
        )
    if length_along_pole < 20.0:
        reject(
            f"length_along_pole {length_along_pole} is under 20mm: the rest bears on the "
            "pole as a line rather than a strip, and rocks on the bench. Raise it to 20.0.",
            param="length_along_pole",
        )

    floor = AXIS_HEIGHT - seat_radius
    if floor < wall_thickness:
        reject(
            f"a pole {pole_diameter} across drops the bottom of the seat to {floor:.1f}mm "
            f"above the bed, under the {wall_thickness}mm floor it needs. This rest is built "
            f"for the {AXIS_HEIGHT}mm axis height the row shares.",
            param="pole_diameter",
        )

    # The seat is the pole's own arc, offset by the clearance, so contact is spread over
    # `wrap_angle` instead of two edges. The horns are where that arc leaves the top face.
    half_wrap = radians(wrap_angle / 2)
    horn_x = seat_radius * sin(half_wrap)
    horn_z = AXIS_HEIGHT - seat_radius * cos(half_wrap)
    width = 2 * (horn_x + wall_thickness)

    body = Pos(0, 0, horn_z / 2) * Box(width, length_along_pole, horn_z)
    seat = (
        Pos(0, 0, AXIS_HEIGHT)
        * Rot(90, 0, 0)
        * Cylinder(seat_radius, length_along_pole + 2 * CHAMFER + 2)
    )
    body = body - seat

    if draft:
        return body

    # The seat is mating geometry and the bottom is the bed, so neither gets a facet.
    # A lead-in at the mouth would only shorten the arc that carries the pole.
    bed = body.bounding_box().min.Z

    def on_seat(edge):
        point = edge @ 0.5
        return abs(hypot(point.X, point.Z - AXIS_HEIGHT) - seat_radius) < 0.01

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > bed + 0.01 and not on_seat(e)
    )
    return polish(body, keep, CHAMFER)
