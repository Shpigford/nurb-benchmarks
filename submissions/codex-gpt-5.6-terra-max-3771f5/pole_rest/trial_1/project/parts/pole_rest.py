from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low, support-free drying rest for one finished pole.

    pole_diameter: outside diameter of the pole supported by the cradle.
    """
    axis_height = 18.0
    radial_clearance = 0.25
    rest_length = 24.0

    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")

    seat_radius = pole_diameter / 2.0 + radial_clearance

    # The top plane exposes roughly 151 degrees of the lower cylindrical seat.
    # That leaves a 120-degree, fully backed central support arc while keeping
    # every part of the mouth below the pole axis for a straight drop-in.
    base_height = axis_height - 0.25 * seat_radius
    base_width = 2.0 * (seat_radius + 2.2)

    base = Box(
        base_width,
        rest_length,
        base_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cutter = (
        Cylinder(
            seat_radius,
            rest_length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.X, 90.0)
        .translate((0.0, 0.0, axis_height))
    )
    return base - cutter
