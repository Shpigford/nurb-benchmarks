from nurb import *


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that traps a cable bundle and screws to the wall with one M4.

    bundle_diameter: measured width of the taped cable bundle
    """
    if bundle_diameter < 4.0:
        reject(
            f"bundle_diameter {bundle_diameter:g} is under 4mm: raise it so the "
            "seat stays printable",
            param="bundle_diameter",
        )

    # Seat is 0.4mm wider than the bundle (8.4 across at the measured 8.0).
    cavity = bundle_diameter + 0.4
    wall = 2.4
    # >= 2.4 of solid along the bore before the pan head seats.
    back = 3.0
    length = 12.0
    screw_hole = 4.4
    driver = 8.4
    ring = 2.8

    cz = wall + cavity / 2.0
    # Front wall covers the bundle's +X side so a 1mm shove away from the wall hits it.
    front_top = cz + 0.5 * bundle_diameter
    # Driver cylinder (8.4) and the installed head must miss the bundle and the lip.
    screw_z = max(
        front_top + 2.0 + driver / 2.0,
        cz + bundle_diameter / 2.0 + 1.0 + driver / 2.0,
    )
    pad_top = screw_z + screw_hole / 2.0 + ring

    loc = (Align.MIN, Align.MIN, Align.MIN)
    back_plate = Pos(0, -length / 2.0, 0) * Box(back, length, pad_top, align=loc)
    floor = Pos(back, -length / 2.0, 0) * Box(cavity + wall, length, wall, align=loc)
    front = Pos(back + cavity, -length / 2.0, 0) * Box(wall, length, front_top, align=loc)
    body = back_plate + floor + front

    # Through-bore along X, opening on the wall face. Lead in both directions
    # so the cut is never coplanar with the plate faces.
    bore = Pos(-1.0, 0, screw_z) * Rot(0, 90, 0) * Cylinder(
        screw_hole / 2.0,
        back + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - bore

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back_x = body.bounding_box().min.X
    hole_r = screw_hole / 2.0 + 0.6
    concave = set(concave_edges(body))

    def keep_edge(e):
        if e in concave:
            return False
        bb = e.bounding_box()
        if bb.min.Z <= bed + 0.05:
            return False
        if bb.min.X <= back_x + 0.05:
            return False
        mid_y = 0.5 * (bb.min.Y + bb.max.Y)
        mid_z = 0.5 * (bb.min.Z + bb.max.Z)
        if abs(mid_y) < hole_r and abs(mid_z - screw_z) < hole_r and bb.size.X < 1.2:
            return False
        return True

    # Only the long rails: 1mm chamfers on three edges at a corner leave
    # ~0.9mm2 triangles, which fail sliver with no card escape.
    keep = body.edges().filter_by(Axis.Y).filter_by(keep_edge)
    return polish(body, keep, 1.0)
