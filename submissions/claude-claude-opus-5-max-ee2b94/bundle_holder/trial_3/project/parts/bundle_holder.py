from math import sqrt

from nurb import *

# ISO 4762 has no pan head, so these are the numbers the screw itself sets: an M4 pan
# head is 8.0 across and 3.2 tall, and the driver wants 0.4 around it to reach the slot.
HEAD_ACROSS = 8.4
HEAD_TALL = 3.2
# Three chamfers meeting at a corner leave a 0.866 * size**2 triangle, so the 1.0mm
# default lands six faces at 0.87mm2 and the sliver rule reads every one as a polish
# bug. 1.1 is the round size whose corners clear the 1mm2 floor, at 1.05mm2 each.
CHAMFER = 1.1


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=1.0,
    holder_length=13.0,
    wall_thickness=3.0,
    lip_grip=1.5,
    screw_hole_width=4.4,
    draft=False,
):
    """An open cradle that carries a cable bundle along a wall on one M4 screw.

    bundle_diameter: how thick the cable bundle is
    bundle_clearance: slack around the bundle so it drops into the cradle
    holder_length: how far the holder runs along the cable
    wall_thickness: how thick the back plate, cradle floor and front lip are
    lip_grip: how far the front lip rises past the middle of the bundle
    screw_hole_width: the clearance hole through the back for the M4 screw
    """
    hole_radius = screw_hole_width / 2
    head_radius = HEAD_ACROSS / 2
    # A loaded hole earns a fastener diameter of wall, and the head has to seat on
    # material rather than on a polish chamfer, so take whichever is thicker.
    boss = max(screw_hole_width - 0.4, head_radius - hole_radius + CHAMFER + 0.5)

    if bundle_clearance < 0.4:
        reject(
            f"bundle_clearance {bundle_clearance} pinches an as-printed bundle instead "
            "of cradling it: raise it to 0.4 or more",
            param="bundle_clearance",
        )
    if holder_length < screw_hole_width + 2 * boss:
        reject(
            f"holder_length {holder_length} leaves no material beside the M4 bore: "
            f"raise it above {screw_hole_width + 2 * boss:.1f}",
            param="holder_length",
        )

    channel = bundle_diameter + bundle_clearance  # the free square the bundle lies in
    depth = 2 * wall_thickness + channel
    floor_top = wall_thickness
    bundle_x = wall_thickness + channel / 2
    bundle_z = floor_top + channel / 2
    # The lip has to reach past the middle of the bundle or a fat bundle rolls over
    # it instead of being held by it, so it is measured from the bundle, not the floor.
    lip_top = bundle_z + lip_grip
    if lip_top < floor_top + 2.0:
        reject(
            f"lip_grip {lip_grip} leaves a lip under 2mm proud of the cradle floor, "
            f"which is a bead rather than a stop: raise it above "
            f"{2.0 + floor_top - bundle_z:.1f}",
            param="lip_grip",
        )

    # The head seats on the front of the back plate and pokes into the cradle, so the
    # bore rides above whichever is higher: the lip the driver swings past, or the
    # bundle's own silhouette where the head reaches furthest from the wall.
    reach = wall_thickness + HEAD_TALL
    offset = max(bundle_x - reach, 0.0)
    over_bundle = bundle_z + sqrt(max((channel / 2) ** 2 - offset**2, 0.0))
    screw_z = max(lip_top, over_bundle) + head_radius + 0.6
    height = screw_z + hole_radius + boss

    corner = (Align.MIN, Align.MIN, Align.MIN)
    body = Box(wall_thickness, holder_length, height, align=corner)
    body += Box(depth, holder_length, wall_thickness, align=corner)
    body += Pos(depth - wall_thickness, 0, 0) * Box(
        wall_thickness, holder_length, lip_top, align=corner
    )
    body = body.clean()
    body -= (
        Pos(wall_thickness / 2, holder_length / 2, screw_z)
        * Rot(0, 90, 0)
        * Cylinder(hole_radius, wall_thickness + 2)
    )

    if draft:
        return body

    # Keep the wall face, the bed face, the bore and its seat, and every inside corner.
    inside = concave_edges(body)

    def polishable(edge):
        box = edge.bounding_box()
        if box.max.X < 0.01 or box.max.Z < 0.01:
            return False
        if edge.geom_type == GeomType.CIRCLE:
            return False
        return not any(edge.is_same(other) for other in inside)

    return polish(body, body.edges().filter_by(polishable), CHAMFER)
