from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that screws on with one M4 and holds a horizontal cable bundle.

    bundle_diameter: across the taped bundle; the trough is this plus 0.4 mm of clearance.
    """
    inner = bundle_diameter + 0.4
    back = 2.8
    wall_t = 2.8
    floor_t = 2.8
    length = 12.0
    bore = 4.4
    head_r = 4.2
    gap = 2.2

    front_x = back + inner + wall_t
    front_h = floor_t + inner
    screw_z = front_h + gap + head_r
    total_h = screw_z + head_r + 1.2

    back_plate = Pos(back / 2, 0, total_h / 2) * Box(back, length, total_h)
    floor = Pos(front_x / 2, 0, floor_t / 2) * Box(front_x, length, floor_t)
    front = Pos(front_x - wall_t / 2, 0, front_h / 2) * Box(wall_t, length, front_h)
    body = back_plate + floor + front

    hole = Pos(back / 2, 0, screw_z) * Rot(0, 90, 0) * Cylinder(bore / 2, back + 4)
    body = body - hole

    # Structural chamfer on the trough's inside corners (printability + load path).
    trough = [
        e
        for e in concave_edges(body)
        if e.length > length - 1.0 and e.bounding_box().min.Z < front_h
    ]
    if trough:
        body = chamfer(trough, 2.0)

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = keep - concave_edges(body)
    keep = keep.filter_by(lambda e: e.length > 8.0)
    keep = keep.filter_by(lambda e: abs(e.bounding_box().center().Z - screw_z) > bore)
    return polish(body, keep, 1.0)
