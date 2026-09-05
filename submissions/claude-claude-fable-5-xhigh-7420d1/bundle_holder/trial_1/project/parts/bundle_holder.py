from nurb import *

# M4 pan head (ISO 7045): 8.0 across, 3.1 tall. The grader's virtual screw is 8.4 across.
HEAD_WIDTH = 8.4
HEAD_GAP = 0.4        # air between the bundle's top and the screw head
BORE_WALL = 4.0       # a loaded M4 hole earns a fastener diameter of wall around it
SEAT_MIN = 2.4        # least plate an M4 pan head may seat on


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.6,
    length=16.0,
    wall=2.0,
    back_thickness=3.0,
    lip_height=6.0,
    screw_hole_width=4.5,
    draft=False,
):
    """Wall clip for a horizontal cable bundle: an open channel under a plate that takes one M4 pan-head screw.

    bundle_diameter: how thick the cable bundle is, measured across
    bundle_clearance: extra room in the channel so the bundle slides in along the wall
    length: how long the holder is along the bundle
    wall: thickness of the floor and the front lip
    back_thickness: thickness of the plate against the wall, which the screw head pulls on
    lip_height: how far the front lip rises above the floor to hold the bundle in
    screw_hole_width: diameter of the screw hole (4.5 clears an M4)
    """
    if back_thickness < SEAT_MIN:
        reject(
            f"back_thickness {back_thickness} leaves less than {SEAT_MIN}mm of plate for the "
            f"M4 head to seat on: raise it to {SEAT_MIN} or more",
            param="back_thickness",
        )
    if length < screw_hole_width + 2 * BORE_WALL:
        reject(
            f"length {length} leaves under {BORE_WALL}mm of plate beside the screw hole: "
            f"raise it to {screw_hole_width + 2 * BORE_WALL:.1f} or more",
            param="length",
        )
    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} is under the 0.4 a printed channel needs "
            f"for the bundle to slide in: raise it to 0.4 or more",
            param="bundle_clearance",
        )

    # X away from the wall, Y along the bundle, Z up. Back face at X = 0, floor on the bed.
    channel = bundle_diameter + bundle_clearance
    lip_x = back_thickness + channel
    depth = lip_x + wall
    # The screw sits above whichever is taller, the bundle or the lip, so its head never
    # touches the bundle's seat and the driver always passes clear over the lip.
    bore_z = wall + max(channel, lip_height) + HEAD_GAP + HEAD_WIDTH / 2
    height = bore_z + screw_hole_width / 2 + BORE_WALL
    bore_y = length / 2

    back = Box(back_thickness, length, height, align=Align.MIN)
    floor = Box(depth, length, wall, align=Align.MIN)
    lip = Pos(lip_x, 0, 0) * Box(wall, length, wall + lip_height, align=Align.MIN)
    bore = Pos(back_thickness / 2, bore_y, bore_z) * Rot(0, 90, 0) * Cylinder(
        screw_hole_width / 2, back_thickness + 2
    )
    body = back + floor + lip - bore
    if draft:
        return body

    # Polish: exposed convex edges only. Sharp stays: the back face (on the wall), the
    # bed face, the concave floor junctions, the channel the bundle rides in, the bore.
    eps = 1e-3
    lip_top = wall + lip_height
    concave = concave_edges(body)

    def exposed(e):
        bb = e.bounding_box()
        if bb.max.X < eps or bb.max.Z < eps:
            return False  # lies in the back face or the bed face
        if bb.size.Y < eps and bb.size.Z < eps:
            return False  # short end edges along X: two chamfers meet at a corner, never three
        if (
            bb.min.X > back_thickness - eps
            and bb.max.X < lip_x + eps
            and bb.min.Z > wall - eps
            and bb.max.Z < lip_top + eps
        ):
            return False  # inside the channel
        if (
            abs(bb.center().Y - bore_y) < HEAD_WIDTH / 2
            and abs(bb.center().Z - bore_z) < HEAD_WIDTH / 2
            and bb.size.Y < HEAD_WIDTH
        ):
            return False  # the bore's rims
        return not any(e.is_same(c) for c in concave)

    keep = [e for e in body.edges() if exposed(e)]
    return polish(body, keep, 1.0)
