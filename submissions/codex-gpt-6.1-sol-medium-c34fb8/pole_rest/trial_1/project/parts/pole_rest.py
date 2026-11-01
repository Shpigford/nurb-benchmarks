from nurb import *


@part
def pole_rest(pole_diameter=float(measured("pole_diameter")), draft=False):
    """A broad, open cradle for a pole drying along Y.

    pole_diameter: diameter of the pole, with its axis held 18 mm above the bench.
    """
    seat_radius = pole_diameter / 2.0 + 0.2
    axis_height = 18.0
    rest_length = 24.0
    side_thickness = 3.0
    if pole_diameter < 4.0 or seat_radius > axis_height - 2.0:
        reject("pole_diameter must be between 4 and 31.6 mm to retain a 2 mm base at the fixed 18 mm axis", param="pole_diameter")

    body = Box(
        2.0 * (seat_radius + side_thickness), rest_length, axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = Pos(0, 0, axis_height) * Cylinder(
        seat_radius, rest_length + 4.0, rotation=(90, 0, 0),
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    body = body - seat
    if draft:
        return body
    # Keep the cylindrical seat and its end rims exact. Chamfer only the
    # outer long top edges, avoiding tiny corner caps at the cradle lips.
    outer_x = seat_radius + side_thickness
    exposed_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > axis_height - 0.001
        and abs(abs(edge.center().X) - outer_x) < 0.001
    )
    return polish(body, exposed_edges, 1.0)
