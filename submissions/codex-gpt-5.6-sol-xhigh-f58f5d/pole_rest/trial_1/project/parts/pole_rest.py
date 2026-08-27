from math import cos, radians

from nurb import *


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A low, full-width cradle for supporting a freshly finished pole.

    pole_diameter: measured diameter of the pole the rest supports
    """
    axis_height = 18.0
    radial_clearance = 0.2
    seat_arc = 125.0
    seat_radius = pole_diameter / 2.0 + radial_clearance

    if pole_diameter < 12.0 or pole_diameter > 26.0:
        reject(
            "pole_diameter must stay between 12 and 26mm so the seat remains "
            "above the base with enough material behind it",
            param="pole_diameter",
        )

    length = 24.0
    base_thickness = 3.2
    side_backing = 2.4
    base_overhang = 2.0

    # The top plane clips a little more than 120 degrees from the lower half
    # of the circular cut.  Keeping it below the pole's lower surface also
    # leaves the entire vertical insertion path unobstructed.
    half_arc = seat_arc / 2.0
    seat_top = axis_height - seat_radius * cos(radians(half_arc))
    body_width = 2.0 * (seat_radius + side_backing)
    base_width = body_width + 2.0 * base_overhang

    base = Box(
        base_width,
        length,
        base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cradle = Box(
        body_width,
        length,
        seat_top - base_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).translate((0, 0, base_thickness))

    pole_space = (
        Cylinder(
            seat_radius,
            length + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        .rotate(Axis.X, 90)
        .translate((0, 0, axis_height))
    )
    rest = (base + cradle) - pole_space

    if draft:
        return rest

    # These are exterior upright corners only: the bed and circular mating
    # surface stay dimensionally exact.
    upright_edges = rest.edges().filter_by(Axis.Z)
    return polish(rest, upright_edges, 1.0)
