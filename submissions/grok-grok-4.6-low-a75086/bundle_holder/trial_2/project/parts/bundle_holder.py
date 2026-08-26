from nurb import *


@part
def bundle_holder(bundle_diameter=8.0, draft=False):
    """Wall-mounted clip for a horizontal cable bundle.

    bundle_diameter: taped bundle across; the pocket is 0.4 mm larger so it fits.
    """
    fit = bundle_diameter + 0.4
    if fit < 4.0:
        reject(
            f"bundle_diameter {bundle_diameter} is too small to print a pocket",
            param="bundle_diameter",
        )

    back = 3.2
    floor = 2.2
    front = 2.0
    length = 12.0
    hole = 4.4
    head = 8.4
    around = 2.6

    screw_z = floor + fit + head / 2.0 + 1.0
    top = screw_z + hole / 2.0 + around
    lip_h = floor + fit

    plate = Box(back, length, top, align=(Align.MIN, Align.CENTER, Align.MIN))
    floor_slab = Box(fit, length, floor, align=(Align.MIN, Align.CENTER, Align.MIN))
    floor_slab = floor_slab.move(Location((back, 0, 0)))
    lip = Box(front, length, lip_h, align=(Align.MIN, Align.CENTER, Align.MIN))
    lip = lip.move(Location((back + fit, 0, 0)))

    body = plate + floor_slab + lip
    inner = concave_edges(body)
    if inner:
        body = fillet(inner, 1.0)

    bore = Cylinder(hole / 2.0, back + 6.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    bore = bore.rotate(Axis.Y, 90)
    bore = bore.move(Location((back / 2.0, 0, screw_z)))
    body = body - bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = []
    for e in body.edges():
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            continue
        c = e.center()
        if abs(c.Z - screw_z) < hole / 2.0 + 1.5 and c.X < back + 0.5:
            continue
        if c.Z > lip_h - 1.6 and c.X > back + fit - 0.5:
            continue
        if c.Z > top - 1.6:
            continue
        keep.append(e)
    return polish(body, keep, 1.0)
