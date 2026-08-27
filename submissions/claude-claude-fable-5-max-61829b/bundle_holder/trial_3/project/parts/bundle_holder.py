from nurb import *

# M4 pan head, ISO 7045 / doctrine fastener table: medium clearance 4.5,
# head-and-driver envelope 8.4 across, head 3.2 tall.
SCREW_CLEARANCE_DIA = 4.5
SCREW_HEAD_DIA = 8.4
SCREW_WALL = 4.0  # a loaded hole earns a fastener diameter of wall


@part
def bundle_holder(bundle_diameter=8.0, holder_length=16.0, draft=False):
    """Wall-mounted cradle for a horizontal cable bundle, fixed by one M4 pan head.

    bundle_diameter: how thick the cable bundle is across
    holder_length: how far the holder runs along the wall
    """
    if bundle_diameter < 1.0:
        reject(
            f"bundle_diameter {bundle_diameter} is under 1mm: a single wire that "
            "thin tapes to the wall, raise it above 1.0",
            param="bundle_diameter",
        )
    if holder_length < 10.0:
        reject(
            f"holder_length {holder_length} is under the 10mm the mount needs to "
            "seat an 8.4mm M4 head with a stable back face: raise it to 10 or more",
            param="holder_length",
        )

    plate = 3.0  # back plate, also the seat depth the screw head bears on
    floor = 2.0  # cradle floor under the bundle
    lip = 2.0  # front lip that blocks the bundle away from the wall
    gap = bundle_diameter + 0.8  # free fit: the bundle drops in every time

    chan_out = plate + gap  # inner face of the lip
    depth = chan_out + lip  # how far the holder stands off the wall
    lip_top = floor + gap / 2 + 0.8  # just past the seated bundle's equator
    # Screw sits above the channel so the driver never crosses the bundle:
    # head edge clears the highest retained bundle position by head_clear.
    screw_z = floor + gap / 2 + bundle_diameter / 2 + SCREW_HEAD_DIA / 2 + 0.6
    height = screw_z + SCREW_CLEARANCE_DIA / 2 + SCREW_WALL

    profile = Polyline(
        (0, 0),
        (depth, 0),
        (depth, lip_top),
        (chan_out, lip_top),
        (chan_out, floor),
        (plate, floor),
        (plate, height),
        (0, height),
        close=True,
    )
    body = extrude(Plane.XZ * make_face(profile), amount=holder_length / 2, both=True)
    bore = Pos(plate / 2, 0, screw_z) * Rot(0, 90, 0) * Cylinder(
        SCREW_CLEARANCE_DIA / 2, plate + 2
    )
    body -= bore

    if draft:
        return body

    # Polish everything except: edges lying in the back or bottom face, concave
    # edges, the bore rims (the seat stays flat), and the channel walls the
    # bundle bears on (no lead-in chamfers on fit geometry).
    tol = 0.01

    def key(e):
        c = e.center()
        return (round(c.X, 3), round(c.Y, 3), round(c.Z, 3))

    skip = {key(e) for e in concave_edges(body)}
    for f in body.faces().filter_by(GeomType.CYLINDER):
        skip |= {key(e) for e in f.edges()}

    def in_channel(bb):
        return (
            bb.min.X > plate - tol
            and bb.max.X < chan_out + tol
            and bb.min.Z > floor - tol
            and bb.min.Z < lip_top + tol
        )

    def lip_top_end(bb):
        # The short lip-top segments on the end faces: chamfering them makes a
        # three-chamfer corner whose cap is a sub-1mm2 sliver, so they stay sharp
        # and the two remaining chamfers miter cleanly.
        return (
            abs(bb.min.Z - lip_top) < tol
            and abs(bb.max.Z - lip_top) < tol
            and bb.max.Y - bb.min.Y < tol
        )

    keep = []
    for e in body.edges():
        bb = e.bounding_box()
        if bb.max.Z < tol:  # lies in the bed face
            continue
        if bb.max.X < tol:  # lies in the wall face
            continue
        if in_channel(bb) or lip_top_end(bb):
            continue
        if key(e) in skip:
            continue
        keep.append(e)
    return polish(body, keep, 1.0)
