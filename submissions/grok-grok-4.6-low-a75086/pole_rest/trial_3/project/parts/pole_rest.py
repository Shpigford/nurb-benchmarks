from nurb import *
from math import cos, radians, sin

AXIS_HEIGHT = 18.0


@part
def pole_rest(
    pole_diameter=measured("pole_diameter"),
    length=22.0,
    wall=2.2,
    gap=0.2,
    draft=False,
):
    """Cradle a freshly finished pole while it dries.

    pole_diameter: width of the pole across
    length: how far the rest runs along the pole
    wall: thickness of the cradle around the pole
    gap: clearance between the pole and the cradle
    """
    pole_diameter = float(pole_diameter)
    r = pole_diameter / 2.0
    inner = r + gap
    if inner >= AXIS_HEIGHT - 1.0:
        reject(
            f"pole_diameter {pole_diameter} puts the cradle through the bed at axis {AXIS_HEIGHT}",
            param="pole_diameter",
        )
    if inner + wall < 2.0:
        reject("wall is too thin to back the cradle", param="wall")

    # Arc a little past 120° so a 1mm polish on the rim still leaves a 120° seat.
    theta = radians(68.0)
    z_top = AXIS_HEIGHT - inner * cos(theta)
    width = 2.0 * ((inner + wall) * sin(theta) + 1.0)
    if width < 16.0:
        width = 16.0
    if length < 20.0:
        reject("length must be at least 20 so the pole can rest across it", param="length")

    body = Pos(0, 0, z_top / 2.0) * Box(width, length, z_top)
    trough = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(inner, length + 4.0)
    body -= trough

    if draft:
        return body

    bed = body.bounding_box().min.Z
    skip = set(concave_edges(body))
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05 and e not in skip
    )
    return polish(body, keep, 1.0)
