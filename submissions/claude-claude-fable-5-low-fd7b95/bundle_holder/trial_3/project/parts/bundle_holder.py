from nurb import *


@part
def bundle_holder(
    bundle_diameter=8.0,
    length=12.0,
    back_thickness=3.0,
    floor_thickness=2.0,
    lip_thickness=2.0,
    draft=False,
):
    """Wall cradle for a horizontal cable bundle, held by one M4 pan-head screw.

    bundle_diameter: how thick the cable bundle is across
    length: how long the holder runs along the bundle
    back_thickness: how thick the wall plate is
    floor_thickness: how thick the shelf under the bundle is
    lip_thickness: how thick the front lip is
    """
    clearance = 0.4
    channel = bundle_diameter + clearance  # 8.4 envelope for an 8.0 bundle
    r = channel / 2.0

    screw_hole = 4.5  # M4 medium clearance
    head = 8.4  # M4 pan head + driver envelope
    boss_margin = 4.2  # solid material around the bore at the seat

    if back_thickness < 2.4:
        reject(
            "back_thickness %.1f is under the 2.4mm the M4 head needs to seat on: raise it"
            % back_thickness,
            param="back_thickness",
        )

    # Bundle axis runs along Y at z_bundle, resting on the floor, against the back.
    z_bundle = floor_thickness + r
    bundle_x = back_thickness + r  # tangent to the back plate's front face

    # Screw sits above the bundle: head (r 4.2) must clear the 8.4 bundle envelope.
    z_screw = z_bundle + r + head / 2.0 + 0.2
    plate_height = z_screw + boss_margin

    lip_inner = back_thickness + channel + 0.1
    depth = lip_inner + lip_thickness
    lip_top = z_bundle + 1.2  # catches a 1mm outward pull with margin

    with BuildPart() as bp:
        # back plate against the wall
        with Locations((back_thickness / 2.0, 0, plate_height / 2.0)):
            Box(back_thickness, length, plate_height)
        # floor under the bundle
        with Locations((depth / 2.0, 0, floor_thickness / 2.0)):
            Box(depth, length, floor_thickness)
        # front lip blocking the bundle from pulling off the wall
        with Locations((lip_inner + lip_thickness / 2.0, 0, lip_top / 2.0)):
            Box(lip_thickness, length, lip_top)
        # M4 clearance bore through the back plate, axis along X
        with Locations((back_thickness / 2.0, 0, z_screw)):
            Cylinder(
                screw_hole / 2.0,
                back_thickness,
                rotation=(0, 90, 0),
                mode=Mode.SUBTRACT,
            )

    body = bp.part
    if draft:
        return body

    bed = body.bounding_box().min.Z
    back = body.bounding_box().min.X
    concave = set(concave_edges(body))
    keep = body.edges().filter_by(
        lambda e: e.geom_type == GeomType.LINE  # leave the bore rims alone
        and e.bounding_box().min.Z > bed + 0.01  # nothing on the bed
        and e.bounding_box().max.X > back + 0.01  # nothing lying in the back face
        # the lip's inner top edge stays sharp: chamfering it makes corner slivers
        and not (
            abs(e.bounding_box().min.X - lip_inner) < 0.01
            and abs(e.bounding_box().min.Z - lip_top) < 0.01
        )
        # the plate's short top side edges make corner slivers where their
        # chamfers meet the front-top chamfer; leave them to the corner blend
        and not (
            e.bounding_box().min.Z > plate_height - 0.01
            and e.length < length - 0.01
        )
        and e not in concave
    )
    return polish(body, keep, 1.0)
