from nurb import *


@part
def pole_rest(pole_diameter=20.0, draft=False):
    """A broad, open cradle for a pole drying along the bench.

    pole_diameter: measured width of the pole, with 0.2 mm radial clearance.
    """
    # The recorded measurement establishes the default; the parameter permits
    # other pole sizes without changing the shared 18 mm axis height.
    measured("pole_diameter")
    axis_height = 18.0
    seat_radius = pole_diameter / 2.0 + 0.2
    rest_length = 24.0
    if pole_diameter < 12.0 or pole_diameter > 28.0:
        reject("Use a pole diameter from 12 to 28 mm to retain the grounded seat.",
               param="pole_diameter")

    body = Box(pole_diameter + 6.0, rest_length, axis_height,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = Pos(0, 0, axis_height) * Cylinder(
        seat_radius, rest_length + 4.0, rotation=(90, 0, 0)
    )
    body = body - seat
    if draft:
        return body
    # Chamfer the two outside top rails only. Chamfering the circular seat ends
    # and lip together produces tiny corner faces and shortens the bearing arc.
    half_width = (pole_diameter + 6.0) / 2.0
    exposed_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > axis_height - 0.001
        and abs(abs(edge.center().X) - half_width) < 0.001
    )
    return polish(body, exposed_edges, 1.0)
