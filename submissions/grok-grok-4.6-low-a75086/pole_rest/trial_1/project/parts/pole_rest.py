from nurb import *

# Pole axis sits this high in Z, centred in X, running along Y.
AXIS_HEIGHT = 18.0
# Soft finish: cradle close to the pole without touching it.
GAP = 0.2
WALL = 2.4
LENGTH = 24.0


@part
def pole_rest(pole_diameter=measured("pole_diameter"), draft=False):
    """Rest that cradles a freshly finished pole while it dries.

    pole_diameter: across the finished pole this rest holds.
    """
    radius = pole_diameter / 2.0
    inner = radius + GAP
    outer = inner + WALL
    floor = AXIS_HEIGHT - outer
    if floor < 0.6:
        reject(
            f"pole_diameter {pole_diameter} leaves the cradle through the bed; "
            f"keep it under {(AXIS_HEIGHT - WALL - GAP - 0.6) * 2:.1f}",
            param="pole_diameter",
        )

    with BuildPart() as bp:
        with Locations((0, 0, AXIS_HEIGHT / 2)):
            Box(2 * outer, LENGTH, AXIS_HEIGHT)
        with Locations((0, 0, AXIS_HEIGHT)):
            Cylinder(
                inner,
                LENGTH + 4,
                rotation=(90, 0, 0),
                mode=Mode.SUBTRACT,
            )
    body = bp.part

    if draft:
        return body
    bed = body.bounding_box().min.Z

    def keep_edge(e):
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        # End-arcs of the trough: polishing them against the top rim leaves slivers.
        dz = bb.max.Z - bb.min.Z
        dx = bb.max.X - bb.min.X
        if dz > 2.0 and dx > 2.0:
            return False
        return True

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
