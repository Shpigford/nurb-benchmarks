from nurb import *

# Room the screw head and a driver socket need in front of the seat, M4 pan head.
HEAD_ROOM = 8.4
# Air between the head's clearance disc and everything below it.
HEAD_GAP = 0.6


@part
def bundle_holder(
    bundle_diameter=8.0,
    bundle_clearance=1.0,
    holder_length=12.0,
    wall_thickness=2.4,
    back_thickness=3.0,
    screw_hole_width=4.4,
    chamfer_size=1.0,
    draft=False,
):
    """Wall cradle for a horizontal cable bundle, held by one M4 screw above it.

    bundle_diameter: how thick the cable bundle is across
    bundle_clearance: extra slack across the cradle so the bundle drops in
    holder_length: how much of the bundle the cradle wraps, along the bundle
    wall_thickness: how thick the cradle floor and its front lip are
    back_thickness: how thick the plate against the wall is, and how long the screw bore
    screw_hole_width: clearance hole for the mounting screw, M4 medium fit
    chamfer_size: chamfer on the exposed edges
    """
    bundle_radius = bundle_diameter / 2.0
    cradle = bundle_diameter + bundle_clearance

    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} leaves no room to drop a "
            f"{bundle_diameter}mm bundle in: raise it to 0.4 or more",
            param="bundle_clearance",
        )
    if back_thickness < 2.4:
        reject(
            f"back_thickness {back_thickness} is under the 2.4mm of bore an M4 head "
            "needs to seat against: raise it to 2.4 or more",
            param="back_thickness",
        )
    if wall_thickness < 2.0:
        reject(
            f"wall_thickness {wall_thickness} is under the 2mm floor for a printed "
            "wall: raise it to 2.0 or more",
            param="wall_thickness",
        )
    if holder_length < screw_hole_width + 6.0:
        reject(
            f"holder_length {holder_length} leaves under 3mm of plate around the "
            f"{screw_hole_width}mm screw hole: raise it above {screw_hole_width + 6.0}",
            param="holder_length",
        )

    # x runs out from the wall, y along the bundle, z up off the bed.
    lip_inner = back_thickness + cradle
    depth = lip_inner + wall_thickness
    bundle_z = wall_thickness + cradle / 2.0
    # The lip stands as high as the bundle, so the cable has to be sprung in.
    lip_top = bundle_z + bundle_radius
    # The head's clearance disc clears both the lip and the bundle by HEAD_GAP.
    screw_z = lip_top + HEAD_ROOM / 2.0 + HEAD_GAP
    cap_radius = holder_length / 2.0

    # The cradle: floor and front lip, one closed section in the xz plane swept the
    # length of the holder. The inside corners stay sharp: the bundle weighs grams,
    # so a relief here would be cosmetic polish in a concave junction.
    section = Polygon(
        (back_thickness, 0.0),
        (depth, 0.0),
        (depth, lip_top),
        (lip_inner, lip_top),
        (lip_inner, wall_thickness),
        (back_thickness, wall_thickness),
        align=None,
    )
    cradle_body = extrude(Plane.XZ * section, amount=-holder_length)

    # The plate against the wall, rounded over the screw so the material around the
    # bore is the same all the way round.
    plate = Pos(back_thickness / 2.0, holder_length / 2.0, screw_z / 2.0) * Box(
        back_thickness, holder_length, screw_z
    )
    cap = Pos(back_thickness / 2.0, holder_length / 2.0, screw_z) * Rot(0.0, 90.0, 0.0) * Cylinder(
        cap_radius, back_thickness
    )

    body = cradle_body + plate + cap

    bore = Pos(back_thickness / 2.0, holder_length / 2.0, screw_z) * Rot(
        0.0, 90.0, 0.0
    ) * Cylinder(screw_hole_width / 2.0, back_thickness + 2.0)
    body = body - bore

    if draft:
        return body

    box = body.bounding_box()
    bed, wall_face = box.min.Z, box.min.X
    inside = {_edge_key(e) for e in concave_edges(body)}
    seat_radius = screw_hole_width / 2.0 + 0.2

    def polishable(edge):
        b = edge.bounding_box()
        # Nothing lying in the wall face or in the bed face.
        if b.max.X - wall_face < 0.01 or b.max.Z - bed < 0.01:
            return False
        # The screw seat is mating geometry: a chamfered mouth is a smaller seat, so
        # the whole bore mouth stays sharp. Test the edge's extent, not its corners.
        if (
            abs(b.min.Y - holder_length / 2.0) <= seat_radius
            and abs(b.max.Y - holder_length / 2.0) <= seat_radius
            and abs(b.min.Z - screw_z) <= seat_radius
            and abs(b.max.Z - screw_z) <= seat_radius
        ):
            return False
        return _edge_key(edge) not in inside

    return polish(body, body.edges().filter_by(polishable), chamfer_size)


def _edge_key(edge):
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4), round(edge.length, 4))
