from nurb import *

# M4 pan head: ISO 273 medium clearance bore; head number is head-plus-driver room.
SCREW_BORE = 4.5
SCREW_HEAD = 8.4
RELIEF = 2.0  # structural inside-corner chamfer at the pocket floor
CHAMFER = 1.2  # 1.0 leaves the three-chamfer corner triangles under the 1mm2 sliver bar


@part
def bundle_holder(bundle_diameter=measured("bundle_diameter"), length=12.0,
                  wall=2.8, draft=False):
    """Wall clip for a horizontal cable bundle, held by one M4 screw.

    bundle_diameter: how wide the cable bundle is across
    length: how long the clip runs along the bundle
    wall: how thick the clip's back, shelf and lip are
    """
    if bundle_diameter < 1.0:
        reject("bundle_diameter under 1mm is thinner than a single cable: "
               "raise it to the bundle's real width", param="bundle_diameter")
    if wall < 2.0:
        reject("wall under 2mm prints as perimeters with nothing inside: "
               "keep it at 2 or more", param="wall")

    pocket = bundle_diameter + 0.6      # bundle plus threading clearance
    floor_z = wall                      # pocket floor, top of the shelf
    lip_x = wall + pocket               # inner face of the front lip
    front_x = lip_x + wall
    lip_top = floor_z + pocket / 2 + 0.7    # lip ends just past the bundle equator
    screw_z = floor_z + bundle_diameter + 5.6   # head clears a seated bundle
    top_z = screw_z + SCREW_HEAD / 2 + CHAMFER + 0.4  # full head seat above the top chamfer

    corner = (Align.MIN, Align.MIN, Align.MIN)
    back = Box(wall, length, top_z, align=corner)
    shelf = Box(front_x, length, floor_z, align=corner)
    lip = Pos(lip_x, 0, 0) * Box(wall, length, lip_top, align=corner)
    body = (back + shelf + lip).clean()

    # Relieve the two loaded valleys where shelf meets back and lip.
    body = chamfer(concave_edges(body), RELIEF)

    body -= Pos(wall / 2, length / 2, screw_z) * Rot(0, 90, 0) * Cylinder(
        SCREW_BORE / 2, wall + 2)

    if draft:
        return body

    valleys = [e.center() for e in concave_edges(body)]

    def polishable(e):
        bb = e.bounding_box()
        c = e.center()
        if bb.max.Z < 0.01:     # lies in the bed face
            return False
        if bb.max.X < 0.01:     # lies in the face against the wall
            return False
        if any((c - v).length < 0.05 for v in valleys):
            return False        # concave edges stay sharp
        if (bb.max.X < wall + 0.01 and abs(c.Y - length / 2) < SCREW_HEAD / 2
                and abs(c.Z - screw_z) < SCREW_HEAD / 2):
            return False        # bore rims: the screw's seat stays flat
        return True

    keep = body.edges().filter_by(polishable)
    return polish(body, keep, CHAMFER)
