from nurb import *

@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), draft=False):
    """Wall clip that holds a horizontal cable bundle with one M4 pan-head screw.

    bundle_diameter: taped bundle width the clip is sized for
    """
    clearance = 0.4
    seat = bundle_diameter + clearance
    back = 4.6
    wall = 2.2
    floor = 2.2
    length = 12.0
    bore = 4.4
    around = 2.8

    inner_x0 = back
    inner_z0 = floor
    channel_top = floor + seat
    outer_x = back + seat + wall
    outer_z = channel_top

    screw_z = channel_top + around + bore / 2.0
    tab_top = screw_z + bore / 2.0 + around
    screw_y = length / 2.0

    body = Box(outer_x, length, outer_z, align=(Align.MIN, Align.MIN, Align.MIN))
    pocket = Box(
        seat,
        length + 2.0,
        seat + 1.0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    pocket = Pos(inner_x0, -1.0, inner_z0) * pocket
    body = body - pocket

    tab = Box(back, length, tab_top - outer_z, align=(Align.MIN, Align.MIN, Align.MIN))
    tab = Pos(0, 0, outer_z) * tab
    body = body + tab

    bore_cut = Cylinder(bore / 2.0, back + 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    bore_cut = Pos(-1.0, screw_y, screw_z) * Rot(Y=90) * bore_cut
    body = body - bore_cut

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed + 0.05)
    keep = keep - concave_edges(body)
    keep = keep - body.edges().filter_by(GeomType.CIRCLE)
    keep = keep.filter_by(lambda e: e.length > 4.0)
    keep = keep.filter_by(lambda e: e.bounding_box().max.Z < tab_top - 0.15)
    return polish(body, keep, 1.0)
