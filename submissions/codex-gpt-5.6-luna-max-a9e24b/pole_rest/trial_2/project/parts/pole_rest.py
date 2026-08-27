from nurb import *


@part
def pole_rest(
    pole_diameter: float = measured("pole_diameter"),
):
    """A support-free drying rest for a finished pole.

    pole_diameter: diameter of the pole being held
    """
    axis_height = 18.0
    radius = pole_diameter / 2.0
    clearance = 0.15
    seat_radius = radius + clearance

    # The opening is deliberately below the pole centre.  At the final
    # position the pole therefore clears both lips while the lower arc stays
    # close enough to cradle it.
    lip_height = axis_height - 0.35 * radius
    footprint_width = pole_diameter + 4.0
    rest_length = 30.0

    body = Box(
        footprint_width,
        rest_length,
        lip_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = Pos(0, 0, axis_height) * Rot(90, 0, 0) * Cylinder(
        seat_radius,
        rest_length + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )

    result = body - seat
    return result
