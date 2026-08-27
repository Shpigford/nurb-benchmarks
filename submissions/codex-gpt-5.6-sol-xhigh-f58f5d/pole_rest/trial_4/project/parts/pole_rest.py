from math import cos, radians

from nurb import *


@part
def pole_rest(pole_diameter: float = 20.0):
    """A soft-finish drying rest with a broad, drop-in cradle.

    pole_diameter: measured diameter of the pole the cradle supports
    """
    axis_height = 18.0
    clearance = 0.2
    cradle_span = 150.0
    backing = 2.4
    length = 24.0

    pole_radius = pole_diameter / 2.0
    seat_radius = pole_radius + clearance
    half_span = cradle_span / 2.0

    body_width = 2.0 * (seat_radius + backing)
    body_height = axis_height - seat_radius * cos(radians(half_span))

    body = Box(body_width, length, body_height).translate(
        (0.0, 0.0, body_height / 2.0)
    )
    channel = (
        Cylinder(seat_radius, length + 2.0)
        .rotate(Axis.X, -90.0)
        .translate((0.0, 0.0, axis_height))
    )

    rest = body - channel
    return polish(rest, rest.edges().filter_by(Axis.Z), 1.0)
