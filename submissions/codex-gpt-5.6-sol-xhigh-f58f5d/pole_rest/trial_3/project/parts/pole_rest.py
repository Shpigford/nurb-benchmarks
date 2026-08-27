from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A support-free saddle for a freshly finished pole.

    pole_diameter: measured width of the pole held by the rest
    """
    axis_height = 18.0
    radial_clearance = 0.2
    backing = 1.2
    rest_length = 24.0

    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")

    pole_radius = pole_diameter / 2.0
    seat_radius = pole_radius + radial_clearance
    if seat_radius + backing >= axis_height:
        reject(
            "pole_diameter is too large to keep the cradle backed above the bed; "
            f"reduce it below {2.0 * (axis_height - backing - radial_clearance):.1f} mm",
            param="pole_diameter",
        )

    # The rim lies 0.49 radii below the axis, producing a 121.3 degree
    # continuous contact arc while remaining completely open from above.
    rest_height = axis_height - 0.49 * seat_radius
    rest_width = pole_diameter + 4.0

    body = Box(
        rest_width,
        rest_length,
        rest_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = Cylinder(
        seat_radius,
        rest_length + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).rotate(Axis.X, 90.0).translate((0.0, 0.0, axis_height))

    cradle = body - seat
    if draft:
        return cradle

    # Soften only the four handled outside corners. The cylindrical seat and
    # its drop-in rim remain dimensionally exact.
    outside_corners = cradle.edges().filter_by(Axis.Z)
    return polish(cradle, outside_corners, 1.0)
