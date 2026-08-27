from math import cos, radians, sin

from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low, support-free cradle for a freshly finished pole.

    pole_diameter: measured width across the pole this rest cradles
    """
    axis_height = 18.0
    pole_clearance = 0.2
    support_half_angle = radians(68.0)
    side_wall = 3.0
    rest_length = 22.0

    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than 0mm", param="pole_diameter")

    seat_radius = pole_diameter / 2.0 + pole_clearance
    cradle_bottom = axis_height - seat_radius
    if cradle_bottom < 3.0:
        reject(
            "pole_diameter is too large to leave a 3mm base below the fixed 18mm axis",
            param="pole_diameter",
        )

    top_height = axis_height - seat_radius * cos(support_half_angle)
    half_width = seat_radius * sin(support_half_angle) + side_wall

    body = Box(
        2.0 * half_width,
        rest_length,
        top_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pole_space = (
        Cylinder(
            seat_radius,
            rest_length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.X, 90.0)
        .translate((0.0, 0.0, axis_height))
    )
    rest = body - pole_space

    if draft:
        return rest

    outside_corners = rest.edges().filter_by(Axis.Z)
    return polish(rest, outside_corners, 1.0)
