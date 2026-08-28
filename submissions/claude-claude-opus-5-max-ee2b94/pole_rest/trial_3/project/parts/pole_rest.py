from math import cos, radians, sin

from nurb import *

# The bench sets this, not the part: several identical rests stand in a row and
# one pole lies across all of them, so every seat has to put the axis at the
# same height. It is an interface, so it is a constant rather than a slider.
POLE_AXIS_HEIGHT = 18.0

# 1.2 rather than the usual 1.0 so the triangle where three chamfers meet at a
# corner lands at 1.25mm2, above the 1mm sliver floor. See the card.
CHAMFER = 1.2

# Solid floor under the deepest point of the cradle.
FLOOR_MIN = 3.0

TOL = 1e-6


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    seat_clearance=0.25,
    cradle_angle=150.0,
    wall_thickness=3.0,
    rest_length=22.0,
    draft=False,
):
    """A cradle that carries a freshly finished pole while it dries.

    pole_diameter: how wide the pole is across
    seat_clearance: the gap between the pole and the cradle it lies in
    cradle_angle: how far around the pole the cradle wraps, in degrees
    wall_thickness: how much material sits behind the cradle at its thinnest
    rest_length: how much of the pole one rest holds, along the pole
    """
    if cradle_angle > 180.0:
        reject(
            f"cradle_angle {cradle_angle:.0f} curls the cradle over the top of the "
            "pole: the pole could no longer be lowered straight in, and the "
            "overhanging horns would need support. Keep it at 180 or under.",
            param="cradle_angle",
        )
    if cradle_angle < 90.0:
        reject(
            f"cradle_angle {cradle_angle:.0f} is a shallow dish rather than a cradle: "
            "the pole would rest on the two rim edges and dent its soft finish. "
            "Keep it at 90 or over.",
            param="cradle_angle",
        )

    seat_radius = pole_diameter / 2.0 + seat_clearance
    floor = POLE_AXIS_HEIGHT - seat_radius
    if floor < FLOOR_MIN:
        reject(
            f"pole_diameter {pole_diameter:.1f} sinks the bottom of the cradle to "
            f"{floor:.1f}mm above the bench, and the axis height of {POLE_AXIS_HEIGHT:.0f} "
            f"is fixed by the row of rests. Keep it under "
            f"{2.0 * (POLE_AXIS_HEIGHT - FLOOR_MIN - seat_clearance):.1f}.",
            param="pole_diameter",
        )

    half_angle = radians(cradle_angle) / 2.0
    # The block stops exactly where the cradle should: cutting a full cylinder
    # out of a box this tall leaves an arc of precisely `cradle_angle`.
    body_height = POLE_AXIS_HEIGHT - seat_radius * cos(half_angle)
    seat_half_width = seat_radius * sin(half_angle)
    body_width = 2.0 * (seat_half_width + wall_thickness)

    body = Box(
        body_width,
        rest_length,
        body_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = Pos(0, 0, POLE_AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(
        seat_radius, rest_length + 2.0
    )
    body = body - seat

    if draft:
        return body

    bed = body.bounding_box().min.Z
    concave = [e.center() for e in concave_edges(body)]

    def in_cradle(edge):
        # Every point of the edge sits on the seat cylinder: mating geometry,
        # and a chamfer here is a lead-in that spoils the fit it lands on.
        return all(
            (p.X**2 + (p.Z - POLE_AXIS_HEIGHT) ** 2) ** 0.5 <= seat_radius + 0.01
            for p in (edge @ (i / 8.0) for i in range(9))
        )

    def keeper(edge):
        if edge.bounding_box().max.Z < bed + TOL:
            return False  # lies in the bed face
        if in_cradle(edge):
            return False
        return not any((edge.center() - c).length < TOL for c in concave)

    keep = body.edges().filter_by(keeper)
    return polish(body, keep, CHAMFER)
