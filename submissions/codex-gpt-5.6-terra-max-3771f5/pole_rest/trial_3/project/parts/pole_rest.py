from math import cos, radians, sin

from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), rest_length=30.0):
    """A low, open saddle that supports a freshly finished pole.

    pole_diameter: diameter of the pole held by the rest
    rest_length: length of the cradle in the pole's direction
    """
    axis_height = 18.0
    clearance = 0.20
    backing = 3.0
    cradle_angle = 130.0

    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")
    if rest_length < 20.0:
        reject("rest_length must be at least 20.0 mm", param="rest_length")

    seat_radius = pole_diameter / 2.0 + clearance
    half_angle = cradle_angle / 2.0
    # The two shoulder tops stop at the ends of a 130 degree lower arc.
    shoulder_height = axis_height - seat_radius * cos(radians(half_angle))
    # This leaves a 3 mm radial wall at the upper edge of the cradle.
    rest_width = 2.0 * (seat_radius * sin(radians(half_angle)) + backing)

    base = Box(
        rest_width,
        rest_length,
        shoulder_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # A horizontal cylindrical cut makes a concave cradle rather than two edges.
    channel = Cylinder(
        seat_radius,
        rest_length,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).rotate(Axis.X, 90.0).translate((0.0, 0.0, axis_height))
    return base - channel
