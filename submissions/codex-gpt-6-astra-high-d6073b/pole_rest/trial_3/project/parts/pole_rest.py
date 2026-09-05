from nurb import *


@part
def pole_rest(pole_diameter=float(measured("pole_diameter")), draft=False):
    """A bench cradle for a finished pole running along Y.

    pole_diameter: measured width of the pole, with its axis fixed 18 mm above the bed.
    """
    if not 14.0 <= pole_diameter <= 28.0:
        reject("Use a pole diameter between 14 and 28 mm for the fixed 18 mm axis height.",
               param="pole_diameter")

    seat_radius = pole_diameter / 2.0 + 0.2
    width = 2.0 * (seat_radius + 3.0)
    length = 24.0
    axis_height = 18.0

    body = Box(width, length, axis_height,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Pos(0, 0, axis_height) * Cylinder(seat_radius, length + 2.0,
                                            rotation=(90, 0, 0))
    body = body - seat
    if draft:
        return body

    # Leave the entire cylindrical seat and its end rims at their measured fit.
    # Only the outside upright corners and long upper edges receive the polish.
    outside = body.edges().filter_by(
        lambda e: e.geom_type == GeomType.LINE
        and abs(abs(e.center().X) - width / 2.0) < 1e-5
        and e.bounding_box().max.Z > 1e-5
    )
    return polish(body, outside, 1.0)
