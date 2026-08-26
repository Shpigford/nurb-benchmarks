from nurb import *

AXIS_HEIGHT = 18.0  # fixed by the row of rests: the pole's axis sits here above the bed


@part
def pole_rest(pole_diameter=20.0, length=22.0, wall_thickness=2.5, clearance=0.1, draft=False):
    """A cradle that holds a drying pole with its axis 18mm above the bed.

    pole_diameter: how thick the pole is; the cradle is cut just over this size
    length: how long the rest is along the pole
    wall_thickness: how much material sits outside the cradle on each side
    clearance: gap left between the finish and the cradle surface
    """
    r = pole_diameter / 2 + clearance
    if r >= AXIS_HEIGHT - 3.0:
        reject(f"pole_diameter {pole_diameter} leaves under 3mm of floor beneath the pole at an axis height of {AXIS_HEIGHT}", param="pole_diameter")
    # Top face stays below the axis so the opening is widest at the rim: the pole
    # lowers straight in. At 0.4 r below the axis the cradle still wraps ~133 degrees.
    top = AXIS_HEIGHT - 0.4 * r
    width = 2 * r + 2 * wall_thickness
    body = Pos(0, 0, top / 2) * Box(width, length, top)
    cradle = Pos(0, 0, AXIS_HEIGHT) * Rot(90, 0, 0) * Cylinder(r, length + 2)
    body = body - cradle
    if draft:
        return body
    bed = body.bounding_box().min.Z
    # Chamfer the outer edges only; the cradle rim stays sharp so the full arc cradles the pole.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed and abs(e.center().X) > r + 0.5
    )
    return polish(body, keep, 1.0)
