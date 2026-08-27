from nurb import *


@part
def pole_rest(pole_diameter: float = 20.0):
    """A low, open trough that supports a freshly finished pole while it dries.

    pole_diameter: measured diameter of the pole resting in the cradle
    """
    axis_height = 18.0
    clearance = 0.2
    rest_width = pole_diameter + 4.0
    rest_length = 24.0
    seat_radius = pole_diameter / 2.0 + clearance
    # A rim at the axis gives the largest possible drop-in-safe cradle: the
    # complete lower semicircle, independent of the selected pole diameter.
    body_height = axis_height

    body = Box(
        rest_width,
        rest_length,
        body_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    seat = Cylinder(
        seat_radius,
        rest_length + 2.0,
        rotation=(90.0, 0.0, 0.0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    seat = Pos(0.0, 0.0, axis_height) * seat

    cradle = body - seat
    outer_corners = cradle.edges().filter_by(
        lambda edge: edge.bounding_box().max.Z - edge.bounding_box().min.Z
        > body_height - 0.01
    )
    return polish(cradle, outer_corners, 1.0)
