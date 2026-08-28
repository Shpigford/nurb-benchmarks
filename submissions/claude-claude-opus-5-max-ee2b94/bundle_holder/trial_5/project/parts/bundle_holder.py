from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    bundle_clearance=0.8,
    holder_length=14.0,
    wall_thickness=2.4,
    back_thickness=3.0,
    lip_rise=2.0,
    screw_hole_width=4.4,
    screw_head_width=8.4,
    screw_surround=3.0,
    chamfer_size=1.0,
    draft=False,
):
    """A wall clip that cradles a horizontal cable bundle on one M4 screw.

    bundle_diameter: how thick the cable bundle is, measured across
    bundle_clearance: extra room around the bundle so it drops into the cradle
    holder_length: how much of the cable run the cradle grips, along the wall
    wall_thickness: thickness of the cradle floor and the front lip
    back_thickness: thickness of the plate that sits against the wall
    lip_rise: how far the front lip climbs past the middle of the bundle
    screw_hole_width: clearance hole for the M4 screw shank
    screw_head_width: room the screw head and the driver need behind it
    screw_surround: material left all round the screw hole
    chamfer_size: size of the chamfer on the exposed edges
    """
    if bundle_clearance < 0.3:
        reject(
            f"bundle_clearance {bundle_clearance} binds on a printed channel: "
            "raise it to 0.3 or more",
            param="bundle_clearance",
        )

    # The cradle, in the mounted frame: +x is away from the wall, +z is up.
    span = bundle_diameter + bundle_clearance  # clear channel the bundle threads
    back, floor, lip = back_thickness, wall_thickness, wall_thickness
    depth = back + span + lip
    bundle_z = floor + span / 2  # bundle centre, sitting clear of the floor
    wall_top = bundle_z + lip_rise  # both cradle walls stop level, here

    # The screw sits above the cable. A bundle can float anywhere the cradle still
    # catches it, which tops out a diameter above the floor plus a millimetre of
    # ride, so the head and the driver behind it are cleared of that, not of where
    # the bundle happens to rest.
    ear_radius = screw_hole_width / 2 + screw_surround
    bundle_ceiling = wall_thickness + bundle_diameter + 1.0
    screw_z = bundle_ceiling + screw_head_width / 2 + 0.6

    if holder_length < 2 * ear_radius:
        reject(
            f"holder_length {holder_length} is under the {2 * ear_radius:.1f}mm ear "
            "the screw needs, so the ear would hang off the cradle with nothing "
            "under it: lengthen the holder or trim screw_surround",
            param="holder_length",
        )

    # Structural relief where the floor meets each wall: the cable's whole weight
    # turns that corner. Kept under a quarter of the span so the channel still
    # passes a full-width bundle.
    relief = min(2.0, 0.25 * span)

    body = Pos(depth / 2, 0, wall_top / 2) * Box(depth, holder_length, wall_top)
    channel = Plane.XZ * Polygon(
        (back + relief, floor),
        (back + span - relief, floor),
        (back + span, floor + relief),
        (back + span, wall_top + span),
        (back, wall_top + span),
        (back, floor + relief),
        align=None,
    )
    body -= extrude(channel, amount=holder_length, both=True)

    # The mounting ear: the back plate carried up past the bundle, shouldered in
    # at 45 degrees and capped round over the screw.
    taper = min((holder_length - 2 * ear_radius) / 2, max(0.0, screw_z - wall_top - 2.0))
    if taper > 0.01:
        shoulder = ear_radius + taper
        ear = Plane.YZ * Polygon(
            (-shoulder, 0.0),
            (shoulder, 0.0),
            (shoulder, wall_top),
            (ear_radius, wall_top + taper),
            (ear_radius, screw_z),
            (-ear_radius, screw_z),
            (-ear_radius, wall_top + taper),
            (-shoulder, wall_top),
            align=None,
        )
    else:
        ear = Plane.YZ * Polygon(
            (-ear_radius, 0.0),
            (ear_radius, 0.0),
            (ear_radius, screw_z),
            (-ear_radius, screw_z),
            align=None,
        )
    ear += Plane.YZ * Pos(0, screw_z) * Circle(ear_radius)
    body += extrude(ear, amount=back)

    # One M4 through-bore, axis along x, mouth on the wall face.
    body -= (
        Pos(back / 2, 0, screw_z)
        * Rot(0, 90, 0)
        * Cylinder(radius=screw_hole_width / 2, height=back + 4)
    )

    if draft:
        return body

    # Nothing in the wall face or the bed face, and nothing concave: a chamfer on
    # an inside corner adds a feather edge instead of taking a corner off.
    box = body.bounding_box()
    bed, wall = box.min.Z, box.min.X
    inside = {_edge_key(e) for e in concave_edges(body)}
    keep = [
        e
        for e in body.edges()
        if _edge_key(e) not in inside
        and e.bounding_box().max.Z > bed + 1e-6
        and e.bounding_box().max.X > wall + 1e-6
        and not _on_bore(e, screw_z, screw_hole_width / 2)
    ]
    return polish(body, keep, chamfer_size)


def _edge_key(edge):
    c = edge.center()
    return (round(c.X, 4), round(c.Y, 4), round(c.Z, 4), round(edge.length, 4))


def _on_bore(edge, screw_z, radius):
    """The screw bore's own rims: the head seats there, so it stays sharp."""
    box, slack = edge.bounding_box(), radius + 0.05
    return (
        abs(box.min.Y) <= slack
        and abs(box.max.Y) <= slack
        and abs(box.min.Z - screw_z) <= slack
        and abs(box.max.Z - screw_z) <= slack
    )
