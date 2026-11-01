from nurb import *


@part
def pole_rest(pole_diameter=float(measured("pole_diameter")), draft=False):
    """A bench cradle for a freshly finished pole.

    pole_diameter: measured width of the pole being dried.
    """
    if not 16.0 <= pole_diameter <= 26.0:
        reject("Use a pole_diameter between 16 and 26 mm for this 18 mm-high axis.",
               param="pole_diameter")
    seat_radius = pole_diameter / 2.0 + 0.2
    length = 24.0
    width = 2.0 * (seat_radius + 2.8)
    # A seat reaching 70 degrees each side of the bottom: open above,
    # with enough wrap to distribute contact over the soft finish.
    from math import cos, radians
    height = 18.0 - seat_radius * cos(radians(70.0))
    body = Box(width, length, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Pos(0, 0, 18.0) * Cylinder(seat_radius, length + 4.0, rotation=(90, 0, 0))
    body = body - seat
    if draft:
        return body
    # Keep the cylindrical seat and bed exact; soften the two outside shoulders.
    shoulders = body.edges().filter_by(
        lambda e: abs(e.center().X) > width / 2.0 - 0.01
        and abs(e.center().Z - height) < 0.01
    )
    return polish(body, shoulders, 1.0)
