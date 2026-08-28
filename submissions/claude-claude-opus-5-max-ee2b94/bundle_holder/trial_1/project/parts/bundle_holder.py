from nurb import *

# M4 pan head, ISO 7045, plus the room a driver needs around it. Published
# numbers, not guesses; the doctrine's fastener table is the source.
SCREW_HOLE = 4.4          # through-bore for the M4 shank
SCREW_HEAD_DIA = 8.0      # pan head across the flats of its dome
DRIVER_DIA = 8.4          # head plus the swing a bit needs to reach it


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.6,
    holder_length=12.0,
    back_thickness=3.0,
    cradle_thickness=2.8,
    lip_grip=0.6,
    chamfer_size=1.2,
    draft=False,
):
    """A wall cradle that carries a cable bundle running along the wall.

    bundle_diameter: how thick the cable bundle is, measured across
    bundle_clearance: slack across the cradle so the bundle drops in
    holder_length: how far the holder runs along the cable
    back_thickness: thickness of the plate that sits against the wall
    cradle_thickness: thickness of the cradle floor and the front lip
    lip_grip: how far up the bundle the front lip reaches, as a fraction
    chamfer_size: the chamfer taken off every exposed edge
    """
    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} leaves the bundle nothing to "
            "drop into: keep it at 0.4 or more",
            param="bundle_clearance",
        )
    if back_thickness < 2.4:
        reject(
            f"back_thickness {back_thickness} is under the 2.4 of material an M4 "
            "needs along its bore before the head seats: raise it above 2.4",
            param="back_thickness",
        )
    if cradle_thickness < 2.0:
        reject(
            f"cradle_thickness {cradle_thickness} is under the 2mm minimum wall: "
            "raise it above 2.0",
            param="cradle_thickness",
        )
    min_length = DRIVER_DIA + 2 * chamfer_size
    if holder_length < min_length:
        reject(
            f"holder_length {holder_length} leaves no solid seat around the screw "
            f"head: raise it above {min_length:.1f}",
            param="holder_length",
        )

    # The cradle: a channel wide enough to drop the bundle into, floored and
    # fronted so the wall, the floor and the lip box it in on three sides.
    cradle_width = bundle_diameter + bundle_clearance
    depth = back_thickness + cradle_width + cradle_thickness
    lip_top = cradle_thickness + bundle_diameter * lip_grip

    # The screw rides high on the plate, above every height a bundle can be held
    # at. Three cases set the floor. In the cradle the bundle can float a shove
    # off the floor and still be caught, so its crown reaches a shove above the
    # cradle. Hung on the top corner of the lip it reaches a diameter above the
    # lip, which is the deeper of the two. And the driver has to swing over the
    # lip to reach the seat at all. The head clears the highest of the three.
    shove = 1.0
    screw_z = max(
        cradle_thickness + bundle_diameter + shove + SCREW_HEAD_DIA / 2 + 0.4,
        lip_top + bundle_diameter + SCREW_HEAD_DIA / 2 + 0.4,
        lip_top + DRIVER_DIA / 2 + 0.6,
    )
    # Plate top clears the driver, plus the chamfer that will be taken off it,
    # so the seat keeps a solid ring all the way around the bore.
    height = screw_z + DRIVER_DIA / 2 + chamfer_size + 0.4

    plate = Pos(back_thickness / 2, holder_length / 2, height / 2) * Box(
        back_thickness, holder_length, height
    )
    floor = Pos(depth / 2, holder_length / 2, cradle_thickness / 2) * Box(
        depth, holder_length, cradle_thickness
    )
    lip = Pos(depth - cradle_thickness / 2, holder_length / 2, lip_top / 2) * Box(
        cradle_thickness, holder_length, lip_top
    )
    body = plate + floor + lip

    bore = Pos(back_thickness / 2, holder_length / 2, screw_z) * Rot(0, 90, 0) * Cylinder(
        SCREW_HOLE / 2, back_thickness + 4
    )
    body = body - bore

    if draft:
        return body

    # Polish: everything exposed except the wall face, the bed face, the inside
    # of the channel the bundle mates with, and every concave edge.
    tol = 1e-6
    concave = [e.center() for e in concave_edges(body)]
    keep = []
    for edge in body.edges().filter_by(GeomType.LINE):
        bb = edge.bounding_box()
        if bb.max.X <= tol:              # lies in the back face, against the wall
            continue
        if bb.max.Z <= tol:              # lies in the bed face
            continue
        if (
            bb.min.X >= back_thickness - tol
            and bb.max.X <= depth - cradle_thickness + tol
            and bb.max.Z <= lip_top + tol
        ):
            continue                     # inside the channel the bundle sits in
        centre = edge.center()
        if any((centre - c).length < 1e-4 for c in concave):
            continue
        keep.append(edge)
    return polish(body, keep, chamfer_size)
