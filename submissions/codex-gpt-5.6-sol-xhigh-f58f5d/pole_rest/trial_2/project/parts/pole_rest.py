from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low, support-free cradle for a freshly finished pole.

    pole_diameter: measured width across the pole the rest cradles
    """
    axis_height = 18.0
    rest_length = 24.0
    radial_clearance = 0.2

    pole_radius = pole_diameter / 2.0
    inner_radius = pole_radius + radial_clearance

    base_width = pole_diameter + 8.0
    cradle_top = axis_height - 0.34 * inner_radius

    if axis_height - inner_radius < 1.2:
        reject(
            "pole_diameter is too large to keep the pole axis 18mm above the bed; "
            "reduce it to 33.2mm or less",
            param="pole_diameter",
        )

    cavity = (
        Cylinder(
            inner_radius,
            rest_length,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        .rotate(Axis.X, 90.0)
        .translate((0, rest_length / 2.0, axis_height))
    )

    base = Box(
        base_width,
        rest_length,
        cradle_top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return base - cavity
