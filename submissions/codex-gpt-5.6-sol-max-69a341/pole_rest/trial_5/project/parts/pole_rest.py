from math import cos, radians

from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low, drop-in cradle for a freshly finished pole.

    pole_diameter: the measured width across the pole
    """
    axis_height = 18.0
    rest_length = 24.0
    clearance = 0.25
    backing = 3.0
    cradle_arc = 128.0

    pole_radius = pole_diameter / 2.0
    seat_radius = pole_radius + clearance
    half_arc = cradle_arc / 2.0
    rest_height = axis_height - seat_radius * cos(radians(half_arc))
    rest_width = 2.0 * (seat_radius + backing)

    body = Box(
        rest_width,
        rest_length,
        rest_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = (
        Cylinder(
            seat_radius,
            rest_length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.X, 90.0)
        .translate((0.0, 0.0, axis_height))
    )

    cradle = body - seat
    if draft:
        return cradle

    exposed_corners = cradle.edges().filter_by(Axis.Z)
    return polish(cradle, exposed_corners, 1.0)
