from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter")):
    """A grounded cradle for a finished pole.

    pole_diameter: diameter of the pole being dried
    """
    pole_radius = pole_diameter / 2.0
    cradle_radius = pole_radius + 0.15

    length_y = 24.0
    footprint_x = 26.0
    top_z = 15.0
    axis_z = 18.0

    body = Box(
        footprint_x,
        length_y,
        top_z,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    channel = (
        Pos(0, 0, axis_z)
        * Rot(90, 0, 0)
        * Cylinder(
            cradle_radius,
            length_y + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
    )
    return body - channel
