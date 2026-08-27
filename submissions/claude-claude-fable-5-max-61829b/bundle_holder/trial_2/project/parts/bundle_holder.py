from nurb import *

# M4 pan head, ISO 7045: 8mm head; +0.4 covers the driver sweep the mount must clear.
BORE_D = 4.5      # M4 clearance, medium column
HEAD_D = 8.4      # head-and-driver envelope
SEAT_MIN = 2.4    # thread engagement the head needs in front of the wall


def _key(e):
    c = e.center()
    return (round(c.X, 2), round(c.Y, 2), round(c.Z, 2))


@part
def bundle_holder(
    bundle_diameter: float = measured("bundle_diameter"),
    holder_length: float = 13.0,
    draft: bool = False,
):
    """Wall-mounted J-hook for a horizontal cable bundle, held by one M4 pan-head screw.

    bundle_diameter: how wide the cable bundle is across
    holder_length: how far the holder runs along the cables
    """
    if bundle_diameter < 2.0:
        reject(
            "bundle_diameter %.1f is thinner than the cradle can close around: use 2.0 or more"
            % bundle_diameter,
            param="bundle_diameter",
        )
    if holder_length < 10.0:
        reject(
            "holder_length %.1f leaves under 10mm of wall contact: use 10.0 or more"
            % holder_length,
            param="holder_length",
        )

    wall = 2.6                      # one wall everywhere; >= SEAT_MIN keeps the screw seat legal
    pocket = bundle_diameter + 0.6  # bundle drops in, never binds
    lip_x = wall + pocket           # inner face of the retaining lip
    depth = lip_x + wall
    rest_z = wall + 0.2 + bundle_diameter / 2       # bundle centre, settled on the floor
    lip_top = rest_z + 1.2                          # lip reaches past the bundle centreline
    # Screw axis high enough that the installed head and its driver sweep stay clear
    # of both the lip and a bundle riding at the top of the cradle.
    axis_z = wall + bundle_diameter + 0.8 + (HEAD_D + 0.2) / 2
    top_z = axis_z + BORE_D / 2 + 4.0               # a fastener diameter of wall above the bore

    body = Pos(wall / 2, 0, top_z / 2) * Box(wall, holder_length, top_z)
    body += Pos(depth / 2, 0, wall / 2) * Box(depth, holder_length, wall)
    body += Pos(lip_x + wall / 2, 0, lip_top / 2) * Box(wall, holder_length, lip_top)
    body -= Pos(wall / 2, 0, axis_z) * Rot(0, 90, 0) * Cylinder(BORE_D / 2, wall + 2)

    if draft:
        return body

    concave = {_key(e) for e in concave_edges(body)}
    keep = []
    for e in body.edges():
        bb = e.bounding_box()
        if bb.max.X < 0.05:                 # lies in the back face
            continue
        if bb.max.Z < 0.05:                 # lies on the bed
            continue
        if e.geom_type == GeomType.CIRCLE:  # bore rims stay crisp: the head seats here
            continue
        if _key(e) in concave:
            continue
        if (
            abs(bb.min.Z - wall) < 0.05
            and abs(bb.max.Z - wall) < 0.05
            and bb.min.X > wall - 0.05
            and bb.max.X < lip_x + 0.05
        ):
            continue                        # cradle floor: no lead-in into the channel
        if (
            abs(bb.min.Z - bb.max.Z) < 0.01
            and abs(bb.min.Y - bb.max.Y) < 0.01
            and bb.min.Z > wall + 0.05
        ):
            continue                        # short top end edges: a third chamfer at those
            #                                 corners leaves sub-mm2 sliver triangles
        keep.append(e)
    return polish(body, keep, 1.0)
