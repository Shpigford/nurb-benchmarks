from nurb import *

AXIS_HEIGHT = 18.0
CLEARANCE = 0.2
BACKING = 2.4
LENGTH = 24.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """Bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: across the pole; the cradle radius follows this size.
    The pole axis stays 18 mm above the bed, centered in X, running along Y.
    """
    if pole_diameter < 10.0:
        reject(
            "pole_diameter is under 10 mm; raise it so the cradle has room",
            param="pole_diameter",
        )
    radius = pole_diameter / 2.0
    inner = radius + CLEARANCE
    if inner + 1.2 >= AXIS_HEIGHT:
        reject(
            "pole_diameter is too large to sit on an 18 mm axis with backing",
            param="pole_diameter",
        )

    width = 2.0 * (inner + BACKING)
    height = AXIS_HEIGHT
    body = Pos(0, 0, height / 2.0) * Box(width, LENGTH, height)

    cut = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(inner, LENGTH + 4.0)
    body = body - cut

    if draft:
        return body

    bed = body.bounding_box().min.Z
    seat_r2 = (inner + 0.9) ** 2

    def _not_seat(e):
        if e.bounding_box().min.Z <= bed + 0.05:
            return False
        c = e.center()
        return (c.X * c.X + (c.Z - AXIS_HEIGHT) ** 2) > seat_r2

    keep = body.edges().filter_by(_not_seat)
    return polish(body, keep, 1.0)
