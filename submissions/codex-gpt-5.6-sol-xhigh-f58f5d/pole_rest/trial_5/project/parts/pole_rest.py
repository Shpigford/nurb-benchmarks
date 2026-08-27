from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: the measured diameter of the pole resting in the cradle
    """
    axis_height = 18.0
    radial_clearance = 0.2
    backing_thickness = 3.0
    rest_length = 20.0

    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + radial_clearance

    if axis_height - cradle_radius < 2.0:
        reject(
            "pole_diameter is too large to leave a 2mm floor below the cradle; "
            f"lower it below {2.0 * (axis_height - radial_clearance - 2.0):.1f}mm",
            param="pole_diameter",
        )

    body_width = 2.0 * (cradle_radius + backing_thickness)
    body = Box(
        body_width,
        rest_length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    cradle = (
        Cylinder(
            cradle_radius,
            rest_length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.X, 90.0)
        .translate((0.0, 0.0, axis_height))
    )
    rest = body - cradle

    if draft:
        return rest

    outer_vertical_edges = rest.edges().filter_by(Axis.Z)
    return polish(rest, outer_vertical_edges, 1.0)
