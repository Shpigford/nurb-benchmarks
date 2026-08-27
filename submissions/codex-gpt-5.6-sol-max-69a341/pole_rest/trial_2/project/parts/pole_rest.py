from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: the measured width across the pole
    """
    axis_height = 18.0
    radial_clearance = 0.2
    backing_thickness = 2.8
    rest_length = 22.0

    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than 0 mm", param="pole_diameter")

    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + radial_clearance
    if cradle_radius > axis_height - 2.0:
        reject(
            "pole_diameter is too large to leave a 2 mm floor below the fixed 18 mm axis",
            param="pole_diameter",
        )

    rest_width = 2.0 * (cradle_radius + backing_thickness)
    body = Box(
        rest_width,
        rest_length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    cutter_length = rest_length + 2.0
    pole_space = Cylinder(
        cradle_radius,
        cutter_length,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    pole_space = pole_space.rotate(Axis.X, -90.0).translate(
        (0.0, -cutter_length / 2.0, axis_height)
    )
    rest = body - pole_space

    if draft:
        return rest

    # Only the four handled outside corners are polished. The bed perimeter and
    # every edge of the fit-critical cradle remain dimensionally exact.
    outside_corners = rest.edges().filter_by(Axis.Z)
    return polish(rest, outside_corners, 1.0)
