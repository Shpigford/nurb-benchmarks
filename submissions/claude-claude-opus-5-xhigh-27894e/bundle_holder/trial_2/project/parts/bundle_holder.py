from math import sqrt

from nurb import *

BORE = 4.5      # M4 clearance, medium column of the fastener table
DRIVER = 8.4    # what the head and the driver sweep in front of the seat
SEAT = 2.4      # the least material a head can pull against


def _key(edge):
    """An edge's identity by where it sits, so two queries can be compared."""
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4))


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.4,
    wall=2.2,
    back_thickness=3.0,
    mouth_fraction=0.8,
    chamfer_size=1.2,
    draft=False,
):
    """A snap-in channel for a horizontal cable bundle over one M4 screw pad.

    bundle_diameter: how thick the cable bundle is across
    bundle_clearance: slack around the bundle so it drops into the channel
    wall: how thick the floor under the bundle and the front lip are
    back_thickness: how much material the screw head pulls against
    mouth_fraction: how far the lip closes over the bundle, as a share of its width
    chamfer_size: the bevel on exposed edges
    """
    if bundle_diameter < 3.0:
        reject(
            f"bundle_diameter {bundle_diameter} leaves a channel no cable finds: "
            "raise it above 3",
            param="bundle_diameter",
        )
    if wall < 2.0:
        reject(
            f"wall {wall} prints as perimeters with nothing between them: "
            "raise it to 2 or more",
            param="wall",
        )
    if back_thickness < SEAT:
        reject(
            f"back_thickness {back_thickness} is under the {SEAT}mm the M4 head has to "
            f"pull against: raise it above {SEAT}",
            param="back_thickness",
        )
    if not 0.4 <= mouth_fraction <= 0.95:
        reject(
            f"mouth_fraction {mouth_fraction} either shuts the channel or stops holding "
            "the bundle in: keep it between 0.4 and 0.95",
            param="mouth_fraction",
        )

    # The channel is an octagon drawn tangent to the bundle: four square faces and four
    # at 45 degrees, so nothing in it overhangs and every facet reads as one system.
    r = (bundle_diameter + bundle_clearance) / 2.0
    s = r / sqrt(2.0)               # where a 45 degree facet touches the bundle
    back = back_thickness
    xc = back + r                   # the bundle rides against the back wall
    zb = wall                       # floor under it
    zc = zb + r
    x_out = xc + r + wall
    length = max(11.0, bundle_diameter + 4.0)

    c_in = xc + zc + 2 * s          # x + z along the lip's inner 45 degree face
    k_br = xc - zc + 2 * s          # x - z along the floor's front 45 degree facet
    k_bl = xc + zc - 2 * s          # x + z along its back one

    x_it = back + mouth_fraction * bundle_diameter   # the lip tip, over the bundle
    z_lean = c_in - x_it
    # The lip ends in a short vertical face rather than a point: a 45 degree face
    # running into a horizontal one leaves a wedge that measures thinner than it prints.
    tip = max(1.5, chamfer_size + 0.8)
    z_lip = z_lean + tip

    profile = [
        (0.0, 0.0),
        (x_out, 0.0),
        (x_out, z_lip),
        (x_it, z_lip),
        (x_it, z_lean),
        (xc + r, c_in - (xc + r)),
        (xc + r, (xc + r) - k_br),
        (k_br + zb, zb),
        (k_bl - zb, zb),
        (back, k_bl - back),
        (back, z_lip),
        (0.0, z_lip),
    ]
    body = extrude(
        Plane.XZ * Polygon(*profile, align=None), amount=length / 2, both=True
    )

    # The screw stands clear above the lip: the head and its driver swing DRIVER across,
    # and nothing of the part may be inside that sweep once the head has seated.
    screw_z = z_lip + DRIVER / 2 + 0.5
    boss = BORE / 2 + 3.0
    plate_top = screw_z + boss
    gable = screw_z + boss * sqrt(2.0)   # y + z along the plate's 45 degree shoulders
    plate = [
        (-length / 2, 0.0),
        (length / 2, 0.0),
        (length / 2, gable - length / 2),
        (gable - plate_top, plate_top),
        (-(gable - plate_top), plate_top),
        (-length / 2, gable - length / 2),
    ]
    body += extrude(Plane.YZ * Polygon(*plate, align=None), amount=back)
    body -= Pos(back / 2, 0, screw_z) * Rot(0, 90, 0) * Cylinder(BORE / 2, back + 2)

    if draft:
        return body

    # Name what must stay sharp, then let `polish` chamfer whatever the kernel takes.
    tol = 1e-6
    sharp = {_key(e) for e in concave_edges(body)}
    axis = Vector(xc, 0, zc)
    for face in body.faces():
        # Every facet of the channel stands exactly `r` off the bundle's axis. They are
        # what the bundle lies against, so their rim is mating geometry and stays sharp:
        # chamfers running into the channel's inside corners leave slivers.
        centre = face.center()
        if abs(abs(face.normal_at(centre).dot(axis - centre)) - r) < 0.05:
            sharp.update(_key(e) for e in face.edges())

    def polishable(e):
        box = e.bounding_box()
        if box.max.X < tol:      # lies in the back face, which meets the wall
            return False
        if box.max.Z < tol:      # lies in the bed
            return False
        if str(e.geom_type).upper().endswith("CIRCLE"):
            return False         # the bore's rims: a lead-in eats the head's seat
        return _key(e) not in sharp

    return polish(body, body.edges().filter_by(polishable), chamfer_size)
