from nurb import *
from math import cos, radians

AXIS_HEIGHT = 18.0
CLEARANCE = 0.2
WALL = 3.0
LENGTH = 24.0
HALF_ANGLE = 70.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """Rest that cradles a freshly finished pole while it dries.

    pole_diameter: width of the pole this rest holds
    """
    if pole_diameter < 8.0:
        reject(
            f"pole_diameter {pole_diameter} is too small for a printable cradle: raise it to 8 or more",
            param="pole_diameter",
        )

    inner_r = pole_diameter / 2.0 + CLEARANCE
    floor = AXIS_HEIGHT - inner_r
    if floor < WALL:
        reject(
            f"pole_diameter {pole_diameter} leaves less than {WALL}mm of floor under the trough at axis height {AXIS_HEIGHT}: lower it",
            param="pole_diameter",
        )

    half = radians(HALF_ANGLE)
    height = AXIS_HEIGHT - inner_r * cos(half)
    width = 2.0 * (inner_r + WALL)

    body = Box(width, LENGTH, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    bore = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(inner_r, LENGTH + 4.0)
    body = body - bore

    if draft:
        return body

    bed = body.bounding_box().min.Z

    def keep_edge(edge):
        if edge.bounding_box().min.Z <= bed + 0.02:
            return False
        p = edge @ 0.5
        radial = (p.X**2 + (p.Z - AXIS_HEIGHT) ** 2) ** 0.5
        # Leave the trough unchamfered so the cradle radius stays intact.
        if radial < inner_r + 1.0:
            return False
        return True

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
