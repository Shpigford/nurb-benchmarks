from nurb import *


@part
def pole_rest(pole_diameter=float(measured("pole_diameter")), draft=False):
    """A broad, open cradle for a pole drying along the bench.

    pole_diameter: measured width of the pole; the axis stays 18mm above the bed.
    """
    axis_height = 18.0
    seat_radius = pole_diameter / 2.0 + 0.2
    rest_length = 24.0
    side_thickness = 3.0
    if pole_diameter <= 0.0 or seat_radius > axis_height - 3.0:
        reject("Use a pole diameter above 0 and at most 29.6mm to retain a 3mm floor.",
               param="pole_diameter")

    half_width = seat_radius + side_thickness
    body = Box(2.0 * half_width, rest_length, axis_height,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    # A half-cylinder open at its equator: no lip blocks the vertical drop-in.
    # Its radius gives 0.2mm clearance throughout the full semicircular seat.
    seat = Pos(0, 0, axis_height) * Cylinder(
        seat_radius, rest_length + 2.0, rotation=(90, 0, 0))
    body = body - seat
    if draft:
        return body

    # Relieve the long outside shoulders, preserving the entire mating surface
    # and the flat bed. End edges remain square to keep full-length support.
    shoulders = body.edges().filter_by(
        lambda edge: abs(abs(edge.center().X) - half_width) < 1e-6
        and abs(edge.center().Z - axis_height) < 1e-6
        and edge.length > rest_length - 1e-6
    )
    return polish(body, shoulders, 1.0)
