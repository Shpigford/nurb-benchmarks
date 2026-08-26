from nurb import *
import math

AXIS_HEIGHT = 18.0
CLEARANCE = 0.1
BACKING = 1.6
LENGTH = 22.0
# Cradle span from the bottom, under 180 so the pole drops in from above.
HALF_ARC_DEG = 80.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """Drying rest that cradles a finished pole across several copies on the bench.

    pole_diameter: width of the pole; the seat radius and width follow this, axis stays at 18 mm.
    """
    radius = pole_diameter / 2.0
    inner = radius + CLEARANCE
    trough_bottom = AXIS_HEIGHT - inner
    if trough_bottom < 2.0:
        reject(
            f"pole_diameter {pole_diameter} puts the trough through the bed at a 18 mm axis; use a smaller pole",
            param="pole_diameter",
        )

    half = math.radians(HALF_ARC_DEG)
    opening_z = AXIS_HEIGHT - inner * math.cos(half)
    width = 2.0 * (inner + BACKING) + 4.0

    body = Box(width, LENGTH, opening_z)
    body = body.move(Location((0, 0, opening_z / 2.0)))

    seat = Cylinder(inner, LENGTH + 4.0)
    seat = seat.rotate(Axis.X, 90)
    seat = seat.move(Location((0, 0, AXIS_HEIGHT)))
    body = body - seat

    if draft:
        return body

    bed = body.bounding_box().min.Z
    # Chamfer only the outer box corners. The trough rim chamfers into slivers.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05
        and abs(e.center().X) > inner + 1.0
    )
    keep = keep - concave_edges(body)
    return polish(body, keep, 1.0)
