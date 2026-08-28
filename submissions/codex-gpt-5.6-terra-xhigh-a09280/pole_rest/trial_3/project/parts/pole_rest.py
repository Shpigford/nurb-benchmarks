from nurb import *


@part
def pole_rest(pole_diameter: float = measured("pole_diameter")):
    """A low, open-top drying rest for a finished pole.

    pole_diameter: diameter of the pole supported in the cradle

    The pole center is always 18 mm above the print bed. The saddle is a lower
    semicircular band, open above its centerline, so a pole can be lowered
    straight into a broad, padded-by-geometry cradle.
    """
    axis_height = 18.0
    clearance = 0.20
    backing = 1.60
    length = 26.0

    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + clearance
    outer_radius = cradle_radius + backing

    # Vertical outside walls keep the rest entirely support-free while leaving
    # more than the required radial backing behind the circular contact arc.
    # Their top is exactly at the pole axis, so the cradle stays open above.
    base_width = 2.0 * outer_radius

    # Cylinders begin along Z; rotate the cutting cylinder onto Y and put its
    # axis at the specified height. It runs beyond both ends of the rest.
    inner = Cylinder(
        cradle_radius, length + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).rotate(Axis.X, -90).translate(
        (0, -(length + 2.0) / 2.0, axis_height)
    )
    body = Box(
        base_width,
        length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body - inner
