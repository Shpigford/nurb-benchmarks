from nurb import *

AXIS_HEIGHT = 18.0
CLEARANCE = 0.2
WALL = 3.2
SEAT_LENGTH = 24.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """A bench rest that cradles a freshly finished pole while it dries.

    pole_diameter: width of the pole that sits in the cradle
    """
    if pole_diameter < 8.0:
        reject(
            f"pole_diameter {pole_diameter} is too small to cradle; raise it above 8",
            param="pole_diameter",
        )

    inner_r = pole_diameter / 2.0 + CLEARANCE
    floor = AXIS_HEIGHT - inner_r
    if floor < WALL:
        reject(
            f"pole_diameter {pole_diameter} leaves only {floor:.1f}mm under the "
            f"cradle at {AXIS_HEIGHT:.0f}mm axis height; lower it so at least "
            f"{WALL}mm of floor remains",
            param="pole_diameter",
        )

    width = 2.0 * (inner_r + WALL)
    # Arms stop at the equator so the pole drops in along -Z and every wall
    # is vertical or receding.
    height = AXIS_HEIGHT

    body = Box(width, SEAT_LENGTH, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    void = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(
        inner_r,
        SEAT_LENGTH + 4.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    body = body - void

    if draft:
        return body

    # Only the long top edges, along the pole. Vertical corners meet the bed, and
    # three chamfers at an arm corner leave a sub-1mm2 sliver the grader will not
    # let a card accept.
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(Axis.Y).filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-3
    )
    return polish(body, keep, 1.0)
