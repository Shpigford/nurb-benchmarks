"""A broad circular seat for a pole with a delicate finish."""

from math import cos, radians
from nurb import *


@part
def pole_rest(pole_diameter: float = float(measured("pole_diameter")), draft=False):
    """Hold a pole horizontally while its finish dries.

    pole_diameter: measured width of the pole, with its axis fixed 18 mm above the bench
    """
    if not 12.0 <= pole_diameter <= 28.0:
        reject("pole_diameter must be between 12 and 28 mm for the fixed 18 mm axis", param="pole_diameter")

    seat_radius = pole_diameter / 2.0 + 0.2
    seat_height = 18.0 - seat_radius * cos(radians(70.0))
    width = 2.0 * (seat_radius + 2.0)
    length = 24.0

    blank = Box(width, length, seat_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    opening = Pos(0, 0, 18.0) * Rot(90, 0, 0) * Cylinder(seat_radius, length + 4.0)
    body = blank - opening

    if draft:
        return body

    # Preserve the entire circular contact surface and its four rim edges.
    # Chamfer only exterior straight edges, excluding the bed perimeter.
    exterior = body.edges().filter_by(
        lambda edge: edge.geom_type == GeomType.LINE
        and edge.bounding_box().max.Z > 0.001
        and abs(abs(edge.center().X) - width / 2.0) < 0.001
    )
    return polish(body, exterior, 1.0)
