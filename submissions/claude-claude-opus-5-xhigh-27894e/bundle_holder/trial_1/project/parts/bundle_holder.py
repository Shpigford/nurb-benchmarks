from math import sqrt

from nurb import *

# The virtual M4 pan head this holder has to leave room for. The driver socket, not the
# head, is the wide part, so it sets the clear cylinder standing off the seat.
HEAD_WIDTH = 8.4
HEAD_HEIGHT = 3.2
SCREW_CLEARANCE = 0.6


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.8,
    holder_width=13.0,
    back_thickness=3.0,
    base_thickness=2.4,
    lip_thickness=3.2,
    lip_height=6.4,
    screw_hole_width=4.4,
    screw_wall=4.0,
    chamfer_size=1.2,
    draft=False,
):
    """An open trough that carries a horizontal cable bundle on one M4 wall screw.

    bundle_diameter: how thick the cable bundle is, across
    bundle_clearance: how much wider than the bundle the trough runs, so it drops in
    holder_width: how much of the bundle's length the holder grips, along the cable
    back_thickness: how thick the plate that sits against the wall is
    base_thickness: how thick the floor the bundle rests on is
    lip_thickness: how thick the front lip that keeps the bundle in is
    lip_height: how far the front lip rises above the trough floor
    screw_hole_width: the through-hole for the M4 wall screw
    screw_wall: how much plate is left around the screw hole
    chamfer_size: the chamfer taken off exposed edges
    """
    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} leaves the bundle no room to drop in:"
            " raise it to 0.4 or more",
            param="bundle_clearance",
        )
    if screw_hole_width < 4.3:
        reject(
            f"screw_hole_width {screw_hole_width} is under the 4.3mm ISO 273 clearance"
            " for M4: raise it above 4.3",
            param="screw_hole_width",
        )
    if back_thickness < 2.4:
        reject(
            f"back_thickness {back_thickness} leaves the screw head too little plate to"
            " pull against: raise it above 2.4",
            param="back_thickness",
        )
    if lip_height < bundle_diameter / 2:
        reject(
            f"lip_height {lip_height} stops short of the middle of a {bundle_diameter}mm"
            f" bundle, so the bundle rolls out over it: raise it above"
            f" {bundle_diameter / 2}",
            param="lip_height",
        )
    if holder_width < screw_hole_width + 2 * screw_wall:
        reject(
            f"holder_width {holder_width} leaves under {screw_wall}mm of plate beside the"
            f" screw hole: raise it above {screw_hole_width + 2 * screw_wall}",
            param="holder_width",
        )

    trough = bundle_diameter + bundle_clearance
    depth = back_thickness + trough + lip_thickness
    lip_top = base_thickness + lip_height

    # Where the bundle ends up: centred across the trough, floor under it, wall behind.
    bundle_x = back_thickness + trough / 2
    bundle_z = base_thickness + trough / 2
    bundle_radius = bundle_diameter / 2

    # The screw rides above everything it has to miss. Above the lip, so a driver
    # reaches the head straight down the bore from the front; above the bundle, so the
    # installed screw and the cable never want the same millimetre. The second one is
    # the taller: the head only stands HEAD_HEIGHT off the seat, so what matters is how
    # high the bundle has climbed by the time it reaches that far from the wall.
    reach = bundle_x - (back_thickness + HEAD_HEIGHT)
    over_bundle = 0.0
    if abs(reach) < bundle_radius:
        over_bundle = bundle_z + sqrt(bundle_radius**2 - reach**2) + HEAD_WIDTH / 2
    screw_z = max(lip_top + HEAD_WIDTH / 2, over_bundle) + SCREW_CLEARANCE
    back_height = screw_z + screw_hole_width / 2 + screw_wall

    back = Pos(back_thickness / 2, 0, back_height / 2) * Box(
        back_thickness, holder_width, back_height
    )
    base = Pos(depth / 2, 0, base_thickness / 2) * Box(
        depth, holder_width, base_thickness
    )
    lip = Pos(depth - lip_thickness / 2, 0, lip_top / 2) * Box(
        lip_thickness, holder_width, lip_top
    )
    bore = (
        Pos(back_thickness / 2, 0, screw_z)
        * Rot(0, 90, 0)
        * Cylinder(screw_hole_width / 2, back_thickness + 2)
    )

    body = back + base + lip - bore
    if draft:
        return body

    # Nothing lying in the wall plane, nothing lying in the bed plane, nothing concave,
    # and nothing round: the round edges here are the bore's two mouths, and the front
    # one is the annulus the screw head bears on. Nothing lying in the trough floor
    # either, which is the face the bundle beds on and the thinnest slab on the part: a
    # chamfer along its side rim takes the floor under what this printer lays reliably,
    # and buys nothing, because that rim is inside the channel where no hand goes.
    concave = set(concave_edges(body))
    keep = []
    for edge in body.edges():
        if edge in concave:
            continue
        if edge.geom_type != GeomType.LINE:
            continue
        box = edge.bounding_box()
        in_wall = box.max.X < 0.01
        on_bed = box.max.Z < 0.01
        in_trough_floor = (
            box.min.Z > base_thickness - 0.01 and box.max.Z < base_thickness + 0.01
        )
        if in_wall or on_bed or in_trough_floor:
            continue
        keep.append(edge)
    return polish(body, keep, chamfer_size)
