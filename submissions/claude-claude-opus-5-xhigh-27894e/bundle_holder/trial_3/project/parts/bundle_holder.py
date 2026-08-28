from math import sqrt

from nurb import *

# M4 pan head, DIN 7985: 8.0 across the head, 3.2 tall once it seats. The
# driver needs a little more than the head does, so 8.4 is what has to stay
# clear in front of the wall plate.
HEAD_WIDTH = 8.4
HEAD_HEIGHT = 3.2
# Air between the head and whatever it passes, so a driver going in at a slight
# angle still misses the part.
HEAD_GAP = 0.5
# The doctrine's "a loaded hole earns a fastener diameter of wall", for M4.
BOSS_WALL = 4.0


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.5,
    back_thickness=3.0,
    floor_thickness=2.0,
    lip_thickness=3.0,
    lip_rise=3.8,
    holder_length=14.5,
    screw_hole_width=4.4,
    chamfer_size=1.2,
    draft=False,
):
    """A wall cradle that carries a cable bundle on one M4 pan-head screw.

    bundle_diameter: how thick the cable bundle is, measured across
    bundle_clearance: slack around the bundle so it threads through without binding
    back_thickness: material between the wall and the back of the cradle
    floor_thickness: the shelf the bundle rests on
    lip_thickness: how stout the front lip is
    lip_rise: how far the front lip climbs past the middle of the bundle
    holder_length: how much of the cable run the cradle grips, along the bundle
    screw_hole_width: clearance hole for the M4 mounting screw
    chamfer_size: the polish chamfer on exposed edges
    """
    if bundle_clearance < 0.4:
        reject(
            "bundle_clearance under 0.4 pinches the bundle against the cradle: "
            "raise it to 0.4 or more",
            param="bundle_clearance",
        )
    if lip_rise <= 0.0:
        reject(
            "lip_rise at or below 0 leaves no lip to stop the bundle falling out: "
            "raise it above 0",
            param="lip_rise",
        )

    channel = bundle_diameter + bundle_clearance
    x_back = back_thickness
    x_lip = x_back + channel
    depth = x_lip + lip_thickness
    x_axis = x_back + channel / 2.0
    z_axis = floor_thickness + channel / 2.0
    lip_top = z_axis + lip_rise
    y_screw = holder_length / 2.0

    # The screw sits above the cradle because it has nowhere else to go: the
    # bundle runs the whole length in Y, so only height separates the two. The
    # head stands HEAD_HEIGHT proud of the seat, and at that depth the bundle's
    # crest is still climbing, so solve for where it has got to and clear it.
    radius = bundle_diameter / 2.0
    reach = x_axis - (x_back + HEAD_HEIGHT)
    crest = z_axis + (sqrt(radius**2 - reach**2) if abs(reach) < radius else 0.0)
    z_screw = max(crest, lip_top) + HEAD_WIDTH / 2.0 + HEAD_GAP
    height = z_screw + screw_hole_width / 2.0 + BOSS_WALL

    body = Box(depth, holder_length, height, align=(Align.MIN, Align.MIN, Align.MIN))
    # The cradle: a channel open to the sky, so every wall in it prints vertical.
    body -= Pos(x_back, -1.0, floor_thickness) * Box(
        channel, holder_length + 2.0, height, align=(Align.MIN, Align.MIN, Align.MIN)
    )
    # Everything in front of the wall plate stops at the lip, which is what
    # leaves the driver a clear run at the screw.
    body -= Pos(x_lip, -1.0, lip_top) * Box(
        lip_thickness + 1.0,
        holder_length + 2.0,
        height,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    body -= Pos(-1.0, y_screw, z_screw) * Rot(0.0, 90.0, 0.0) * Cylinder(
        screw_hole_width / 2.0,
        x_back + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    if draft:
        return body

    bed = body.bounding_box().min.Z
    back = body.bounding_box().min.X
    tol = 1e-6
    inside = {_edge_key(e) for e in concave_edges(body)}
    bore = screw_hole_width / 2.0 + tol

    def polishable(edge):
        box = edge.bounding_box()
        if box.max.X <= back + tol:  # lies in the face that meets the wall
            return False
        if box.max.Z <= bed + tol:  # lies in the face that meets the bed
            return False
        if (
            floor_thickness - tol <= box.min.Z
            and box.max.Z <= floor_thickness + tol
            and x_back - tol <= box.min.X
            and box.max.X <= x_lip + tol
        ):  # the cradle mouth the bundle threads through, and the floor it thins
            return False
        if (
            box.max.X <= x_back + tol
            and y_screw - bore <= box.min.Y
            and box.max.Y <= y_screw + bore
            and z_screw - bore <= box.min.Z
            and box.max.Z <= z_screw + bore
        ):  # the bore and the seat the screw head bears on
            return False
        return _edge_key(edge) not in inside

    return polish(body, body.edges().filter_by(polishable), chamfer_size)


def _edge_key(edge):
    center = edge.center()
    return (
        round(center.X, 4),
        round(center.Y, 4),
        round(center.Z, 4),
        round(edge.length, 4),
    )
