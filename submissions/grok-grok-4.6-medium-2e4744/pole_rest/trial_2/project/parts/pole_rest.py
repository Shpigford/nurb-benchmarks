from math import cos, radians, sin

from nurb import *

# Finished pole sits with its axis along Y at this height, centered on the rest in X.
AXIS_HEIGHT = 18.0
# Gap to the wet finish: must stay >= 0.1 from the pole and within 0.4 to cradle it.
CLEARANCE = 0.25
# Radial material behind the seat; 1.2 is the mechanical minimum.
WALL = 3.0
# Half of the cradle wrap. 70° each side is 140°, above the 120° the pole needs.
WRAP_HALF_DEG = 70.0
REST_LENGTH = 24.0
# Horizontal strip beside each lip so a 1mm polish chamfer does not thin the wall.
TOP_PAD = 4.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: width of the pole that sits in the cradle
    """
    radius = pole_diameter / 2.0
    inner_r = radius + CLEARANCE
    half = radians(WRAP_HALF_DEG)
    groove_floor = AXIS_HEIGHT - inner_r

    if pole_diameter < 8.0:
        reject(
            f"pole_diameter {pole_diameter} is too small for a printable cradle: raise it above 8",
            param="pole_diameter",
        )
    if groove_floor < 2.0:
        limit = 2.0 * (AXIS_HEIGHT - CLEARANCE - 2.0)
        reject(
            f"pole_diameter {pole_diameter} cuts through the bed under an axis at 18mm: lower it below {limit:.1f}",
            param="pole_diameter",
        )

    inner_lip_x = inner_r * sin(half)
    height = AXIS_HEIGHT - inner_r * cos(half)
    # Wide enough for the lip pad and for WALL of material behind the seat.
    width = 2.0 * max(inner_lip_x + TOP_PAD, (inner_r + WALL) * sin(half))

    block = Pos(0, 0, height / 2.0) * Box(width, REST_LENGTH, height)
    cut = (
        Pos(0, 0, AXIS_HEIGHT)
        * Rot(90, 0, 0)
        * Cylinder(
            inner_r,
            REST_LENGTH + 10.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
    )
    body = block - cut

    if draft:
        return body
    bed = body.bounding_box().min.Z
    cyl_edges = body.faces().filter_by(GeomType.CYLINDER).edges()
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = keep - cyl_edges
    return polish(body, keep, 1.0)
