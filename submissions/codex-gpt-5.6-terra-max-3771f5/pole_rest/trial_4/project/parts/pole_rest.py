from nurb import *


@part
def pole_rest(pole_diameter: float = measured("pole_diameter"), draft=False):
    """A low, open saddle for a freshly finished pole.

    pole_diameter: measured diameter of the pole held in the cradle.
    """
    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")

    # The pole datum is fixed by the drying rack: its axis is always 18 mm over
    # the print bed. A 0.20 mm radial gap keeps the soft finish off the plastic.
    pole_axis_height = 18.0
    radial_clearance = 0.20
    seat_radius = pole_diameter / 2.0 + radial_clearance

    # Opening the saddle 40% of its radius below the axis leaves a 132.8 degree
    # lower arc.
    # That gives the requested 120 degree cradle with margin while remaining
    # completely open above the pole for a straight vertical drop-in.
    saddle_top = pole_axis_height - 0.40 * seat_radius
    rest_width = 2.0 * seat_radius + 6.0
    rest_length = 24.0

    base = Box(
        rest_width,
        rest_length,
        saddle_top,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Make the cylindrical void longer than the base so there are no end walls
    # at the working length of the cradle. Rotating a centered Z cylinder puts
    # its axis along Y, centered in X and exactly at the fixed 18 mm datum.
    seat_cut = Cylinder(
        seat_radius,
        rest_length + 2.0,
        rotation=(90.0, 0.0, 0.0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).translate((0.0, 0.0, pole_axis_height))

    return base - seat_cut
