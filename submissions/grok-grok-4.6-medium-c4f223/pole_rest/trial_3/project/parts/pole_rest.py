from math import cos, radians, sqrt

from nurb import *

# Pole axis is fixed in the world: along Y, 18 mm above the bed, centered in X.
AXIS_HEIGHT = 18.0
# Gap to the wet finish: at least 0.1 so nothing rubs, at most 0.4 so the
# cradle still counts as support along the arc.
GAP = 0.2
# Side walls after the 1 mm polish still have to clear min_wall.
WALL = 3.6
# Along the pole. The cradle runs the full length, well past the two-thirds rule.
LENGTH = 24.0


@part
def pole_rest(pole_diameter=float(measured("pole_diameter")), draft=False):
    """Cradle a freshly finished pole while it dries.

    Several identical rests stand in a row; the pole lies across them along Y
    with its axis 18 mm above the bed, centered on this rest in X.

    pole_diameter: how wide the pole is; the seat scales around the fixed axis
    """
    radius = pole_diameter / 2.0
    if radius <= 1.0:
        reject(
            "pole_diameter is too small to cradle; raise it above 2 mm",
            param="pole_diameter",
        )

    inner_r = radius + GAP
    groove_floor = AXIS_HEIGHT - inner_r
    if groove_floor < 2.4:
        reject(
            f"pole_diameter {pole_diameter} leaves only {groove_floor:.1f} mm under the seat; "
            "keep it small enough that 2.4 mm of rest remains under the pole",
            param="pole_diameter",
        )

    # 120° of support is 60° either side of the bottom. Keep the block above
    # that band and below the axis so the pole drops straight in.
    support_top = AXIS_HEIGHT - inner_r * cos(radians(60.0))
    height = min(AXIS_HEIGHT - 0.8, support_top + 2.5)
    if height < support_top + 1.0:
        reject(
            f"pole_diameter {pole_diameter} cannot form a 120° drop-in cradle "
            "with the axis 18 mm above the bed",
            param="pole_diameter",
        )

    drop = AXIS_HEIGHT - height
    opening = sqrt(inner_r * inner_r - drop * drop)
    half_w = opening + WALL

    base = Box(
        2.0 * half_w,
        LENGTH,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cut = Cylinder(inner_r, LENGTH + 4.0)
    cut = Location((0.0, 0.0, AXIS_HEIGHT)) * Rotation(90.0, 0.0, 0.0) * cut
    body = base - cut

    if draft:
        return body

    # Chamfer the box. Leave the cradle alone: polishing the cylinder lips
    # leaves sliver faces where those chamfers meet the end arcs.
    bed = body.bounding_box().min.Z
    cradle = body.faces().filter_by(GeomType.CYLINDER).edges()
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 0.05 and e not in cradle
    )
    return polish(body, keep, 1.0)
