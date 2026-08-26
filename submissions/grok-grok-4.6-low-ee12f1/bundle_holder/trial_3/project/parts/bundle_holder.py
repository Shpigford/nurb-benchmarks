from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall-mounted clip for a taped cable bundle, one M4 pan-head into the wall.

    bundle_diameter: calipered width of the taped bundle
    """
    if bundle_diameter < 4.0:
        reject("bundle_diameter is under 4mm: raise it", param="bundle_diameter")

    inner = bundle_diameter + 0.4
    wall = 2.4
    back_t = 3.2
    length = 12.0
    hole_r = 2.2
    head_r = 4.2

    floor_z = wall
    channel_top = floor_z + inner
    screw_z = channel_top + 1.2 + head_r
    pad_top = screw_z + hole_r + 2.6
    front_inner = back_t + inner

    back = Pos(back_t / 2, 0, pad_top / 2) * Box(back_t, length, pad_top)
    floor = Pos(back_t + (inner + wall) / 2, 0, wall / 2) * Box(
        inner + wall, length, wall
    )
    front = Pos(front_inner + wall / 2, 0, channel_top / 2) * Box(
        wall, length, channel_top
    )
    body = back + floor + front

    hole = Rot(0, 90, 0) * Cylinder(hole_r, back_t + 4)
    hole = Pos(back_t / 2, 0, screw_z) * hole
    body = body - hole

    if draft:
        return body

    bed = body.bounding_box().min.Z
    banned = concave_edges(body)

    def keep_edge(e):
        if e in banned:
            return False
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        mid = bb.center()
        if (mid.Y**2 + (mid.Z - screw_z) ** 2) ** 0.5 < hole_r + 1.6:
            return False
        if mid.Z > pad_top - 2.0:
            return False
        if mid.Z > channel_top - 1.6 and mid.X > front_inner - 0.2:
            return False
        return True

    keep = body.edges().filter_by(keep_edge)
    return polish(body, keep, 1.0)
