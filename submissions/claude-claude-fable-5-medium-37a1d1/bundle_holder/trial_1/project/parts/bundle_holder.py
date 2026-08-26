from nurb import *


@part
def bundle_holder(
    bundle_diameter=8.0,
    length=14.0,
    back_thickness=3.0,
    floor_thickness=2.4,
    lip_thickness=2.4,
    lip_height=5.0,
    clearance=0.4,
    screw_hole_width=4.4,
    draft=False,
):
    """
    bundle_diameter: how thick the cable bundle is
    length: how long the holder runs along the wall
    back_thickness: how thick the plate against the wall is
    floor_thickness: how thick the shelf under the bundle is
    lip_thickness: how thick the front lip is
    lip_height: how far the front lip rises above the shelf
    clearance: extra room around the bundle so it slides in
    screw_hole_width: diameter of the M4 clearance hole
    """
    if bundle_diameter < 2.0:
        reject("bundle_diameter is too small to hold: raise it above 2", param="bundle_diameter")
    pocket = bundle_diameter + clearance          # room for the bundle
    head_dia = 8.4                                # M4 pan head plus driver
    head_height = 3.2
    # screw axis sits above the bundle so the head never lands on it
    screw_z = floor_thickness + pocket - 2.0 + head_dia / 2 + 0.2
    back_height = screw_z + head_dia / 2 + 4.0    # a fastener diameter of wall past the bore
    reach = back_thickness + pocket + lip_thickness

    # profile in XZ, extruded along Y; back face at x = 0, bed at z = 0
    back = Box(back_thickness, length, back_height, align=(Align.MIN, Align.CENTER, Align.MIN))
    floor = Box(reach, length, floor_thickness, align=(Align.MIN, Align.CENTER, Align.MIN))
    lip = Box(lip_thickness, length, floor_thickness + lip_height,
              align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((reach - lip_thickness, 0, 0)))
    body = back + floor + lip

    # screw bore through the back plate, axis along X
    bore = Cylinder(screw_hole_width / 2, back_thickness + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    bore = bore.rotate(Axis.Y, 90).moved(Location((-1, 0, screw_z)))
    body = body - bore

    if draft:
        return body
    bed = body.bounding_box().min.Z
    keep = body.edges().filter_by(lambda e: e.bounding_box().min.Z > bed)
    keep = keep.filter_by(GeomType.LINE).filter_by(lambda e: abs(e.tangent_at(0).Z) < 0.99)
    keep = keep.filter_by(lambda e: e not in concave_edges(body))
    return polish(body, keep, 1.0)
