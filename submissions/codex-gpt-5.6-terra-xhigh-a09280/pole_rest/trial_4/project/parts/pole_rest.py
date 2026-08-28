from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), rest_length=30.0, draft=False):
    """A support-free drying rest with a long, softly cradling half-round seat.

    pole_diameter: measured diameter of the pole that sits in the cradle
    rest_length: how far the rest runs along the pole
    """
    if pole_diameter <= 0.0:
        reject("pole_diameter must be greater than zero", param="pole_diameter")
    if rest_length < 20.0:
        reject("rest_length must be at least 20.0mm so the pole is supported along its length", param="rest_length")

    # The pole axis is deliberately fixed at z=18.  A 0.2mm radial clearance
    # protects the finish, while the 1.4mm side wall backs the entire lower
    # semicircle.  Opening the seat exactly at the axis leaves the full upward
    # sweep clear for a straight drop-in.
    axis_height = 18.0
    clearance = 0.2
    backing = 1.4
    seat_radius = pole_diameter / 2.0 + clearance

    if axis_height - seat_radius < 1.2:
        reject(
            "pole_diameter is too large for 1.2mm of material below the cradle; use 33.2mm or less",
            param="pole_diameter",
        )

    rest_width = 2.0 * (seat_radius + backing)
    body = Box(
        rest_width,
        rest_length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # The cutter runs past both ends so every section along the printed length
    # has the same 180-degree lower cradle.
    cutter = Pos(0, 0, axis_height) * Cylinder(
        seat_radius,
        rest_length + 2.0,
        rotation=(90, 0, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    return body - cutter
