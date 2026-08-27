"""A support-free cradle for a freshly finished pole."""

from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """pole_diameter: outside diameter of the pole being dried.

    The pole axis is fixed at Z=18.0 mm.  The lower half of a slightly
    oversized cylindrical seat carries the pole through a continuous cradle,
    while the open top keeps the loading path vertical and unobstructed.
    """
    axis_height = 18.0
    rest_length = 24.0
    radial_clearance = 0.15
    side_backing = 2.0

    seat_radius = pole_diameter / 2.0 + radial_clearance
    rest_width = pole_diameter + 2.0 * side_backing

    body = Box(
        rest_width,
        rest_length,
        axis_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    seat = (
        Pos(0, 0, axis_height)
        * Rot(90, 0, 0)
        * Cylinder(
            seat_radius,
            rest_length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
    )

    rest = body - seat

    # Keep the fit-critical cradle and its rim untouched.  The long outside
    # top edges are safe cosmetic edges and give the print a small, consistent
    # break without narrowing the seat.
    if not draft:
        outer_half_width = rest_width / 2.0
        top_edges = rest.edges().filter_by(
            lambda edge: (
                edge.bounding_box().min.Z > axis_height - 0.01
                and abs(abs(edge.bounding_box().center().X) - outer_half_width) < 0.01
                and edge.bounding_box().size.Y > rest_length * 0.9
            )
        )
        rest = polish(rest, top_edges, 1.0)

    return rest
