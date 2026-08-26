from math import sin, cos, radians

from nurb import *


@part
def pole_rest(
    pole_diameter=20.0,
    rest_length=22.0,
    seat_clearance=0.2,
    wall_thickness=2.6,
    draft=False,
):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: how thick the pole is, measured across
    rest_length: how long the rest runs under the pole
    seat_clearance: extra gap between the seat and the pole surface
    wall_thickness: how much material backs the seat at its rim
    """
    axis_height = 18.0
    seat_radius = pole_diameter / 2 + seat_clearance
    if axis_height - seat_radius < 2.0:
        reject(
            f"pole_diameter {pole_diameter} leaves under 2mm of floor below the "
            f"seat with the pole axis fixed at {axis_height}: keep it below "
            f"{2 * (axis_height - 2.0 - seat_clearance)}",
            param="pole_diameter",
        )

    # The seat wraps the pole to 68 degrees each side of bottom dead centre,
    # a 136 degree cradle, so the pole rests on surface rather than edges and
    # still drops straight in from above (the rim stays below the pole axis).
    rim_angle = radians(68.0)
    half_width = seat_radius * sin(rim_angle) + wall_thickness
    top = axis_height - seat_radius * cos(rim_angle)

    body = Box(
        2 * half_width,
        rest_length,
        top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    groove = (
        Pos(0, 0, axis_height)
        * Rot(90, 0, 0)
        * Cylinder(seat_radius, rest_length + 2)
    )
    body = body - groove

    if draft:
        return body

    def clear_of_seat(e):
        c = e.center()
        return (c.X**2 + (c.Z - axis_height) ** 2) ** 0.5 > seat_radius + 1.0

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > 1e-6 and clear_of_seat(e)
    )
    # 1.2mm rather than the 1mm default: the corner triangles where three
    # chamfers meet then sit above the 1mm2 sliver threshold.
    return polish(body, keep, 1.2)
