from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=1.0,
    holder_length=12.0,
    wall_thickness=2.4,
    back_thickness=3.0,
    lip_reach=2.5,
    screw_hole_width=4.4,
    screw_head_width=8.4,
    driver_gap=0.5,
    chamfer_size=1.2,
    draft=False,
):
    """A wall cradle that carries a horizontal cable bundle on one M4 screw.

    bundle_diameter: how thick the cable bundle is, measured across
    bundle_clearance: extra room around the bundle so it drops into the cradle
    holder_length: how far the holder runs along the cable
    wall_thickness: how thick the cradle floor, front wall and lip are
    back_thickness: how thick the plate that sits against the wall is
    lip_reach: how far the front lip hooks back over the bundle
    screw_hole_width: the hole the M4 screw passes through
    screw_head_width: how much room the screw head and a driver need
    driver_gap: spare room kept between the driver and the lip
    chamfer_size: the chamfer taken off every exposed edge
    """
    if back_thickness < 2.4:
        reject(
            f"back_thickness {back_thickness} is under the 2.4mm of bore an M4 head "
            "needs to seat against: raise it to 2.4 or more",
            param="back_thickness",
        )
    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} leaves the bundle no room to drop "
            "into the cradle: raise it above 0.4",
            param="bundle_clearance",
        )

    seat_width = screw_head_width + 2 * chamfer_size + 0.8
    if holder_length < seat_width:
        reject(
            f"holder_length {holder_length} leaves no seat beside the screw head: "
            f"raise it above {seat_width}",
            param="holder_length",
        )

    opening = bundle_diameter + bundle_clearance
    if lip_reach > opening - 2.0:
        reject(
            f"lip_reach {lip_reach} shuts the mouth of a {opening}mm cradle: "
            f"lower it below {opening - 2.0}",
            param="lip_reach",
        )

    floor_top = wall_thickness
    cradle_top = floor_top + opening
    lip_top = cradle_top + lip_reach
    front_x = back_thickness + opening
    depth = front_x + wall_thickness

    # A driver has to reach the screw, so nothing forward of the wall plate may stand
    # within half a head of the axis. The lip is the tallest thing forward, so it sets
    # the screw height; the plate then carries a full head of seat above the bore.
    screw_height = lip_top + screw_head_width / 2 + driver_gap
    height = screw_height + screw_head_width / 2 + chamfer_size + 0.4

    profile = Plane.XZ * Polygon(
        (0.0, 0.0),
        (depth, 0.0),
        (depth, lip_top),
        (front_x - lip_reach, lip_top),
        (front_x, cradle_top),
        (front_x, floor_top),
        (back_thickness, floor_top),
        (back_thickness, height),
        (0.0, height),
        align=None,
    )
    body = extrude(profile, amount=holder_length / 2, both=True)

    bore = (
        Pos(back_thickness / 2, 0.0, screw_height)
        * Rot(0.0, 90.0, 0.0)
        * Cylinder(screw_hole_width / 2, back_thickness * 3)
    )
    body -= bore

    if draft:
        return body

    box = body.bounding_box()
    back, bed = box.min.X, box.min.Z
    concave = {_edge_key(e) for e in concave_edges(body)}
    keep = [
        e
        for e in body.edges()
        # An edge lying in the wall face or the bed face buys nothing by being cut.
        if e.bounding_box().max.X > back + 1e-6
        and e.bounding_box().max.Z > bed + 1e-6
        # The bore mouth and the seat the head bears on stay as modelled.
        and e.geom_type != GeomType.CIRCLE
        and _edge_key(e) not in concave
    ]
    return polish(body, keep, chamfer_size)


def _edge_key(edge):
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4), round(edge.length, 4))
