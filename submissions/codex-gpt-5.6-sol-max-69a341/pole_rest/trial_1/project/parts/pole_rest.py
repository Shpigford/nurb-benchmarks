from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low, full-length cradle for a freshly finished pole.

    pole_diameter: the measured diameter of the pole the rest cradles
    """
    axis_height = 18.0
    radial_clearance = 0.2
    seat_radius = pole_diameter / 2.0 + radial_clearance

    # The rim sits just above the 120-degree chord of the circular seat.
    # Keeping it below the pole centre leaves a completely vertical drop-in path.
    body_height = axis_height - 0.49 * seat_radius
    body_width = 2.0 * seat_radius + 9.6
    body_length = 24.0

    body = Box(
        body_width,
        body_length,
        body_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = (
        Cylinder(
            seat_radius,
            body_length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.X, 90.0)
        .translate((0.0, 0.0, axis_height))
    )

    cradle = body - seat
    if draft:
        return cradle

    # Dress only the four handled outside corners. The circular seat and its
    # mouth remain exact fit geometry, and the bed face stays full-size.
    outside_corners = cradle.edges().filter_by(
        lambda edge: (
            edge.bounding_box().size.Z > body_height - 0.01
            and edge.bounding_box().size.X < 0.01
            and edge.bounding_box().size.Y < 0.01
            and abs(edge.center().X) > body_width / 2.0 - 0.01
            and abs(edge.center().Y) > body_length / 2.0 - 0.01
        )
    )
    return polish(cradle, outside_corners, 1.0)
