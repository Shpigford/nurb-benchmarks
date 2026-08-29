from nurb import *


@part
def bundle_holder(
    bundle_diameter=measured("bundle_diameter"),
    slack_around_bundle=0.5,
    holder_width=14.0,
    back_thickness=3.0,
    hook_thickness=3.0,
    lip_overhang=1.5,
    screw_hole_width=4.5,
    draft=False,
):
    """A wall hook that cradles a cable bundle and keeps it from sagging.

    bundle_diameter: how thick the taped cable bundle is
    slack_around_bundle: extra room in the channel so the bundle slides freely
    holder_width: how wide the holder is along the wall
    back_thickness: how thick the plate against the wall is
    hook_thickness: how thick the hook floor and arm are
    lip_overhang: how far the arm tip leans back over the channel to trap the bundle
    screw_hole_width: how wide the hole for the M4 wall screw is
    """
    channel = bundle_diameter + slack_around_bundle
    if lip_overhang < 0.8:
        lip_overhang = 0.0  # under a chamfer's minimum it is a sliver, not a lip
    entry_gap = channel - lip_overhang
    if entry_gap < bundle_diameter * 0.7:
        reject(
            f"lip_overhang {lip_overhang} closes the entry to {entry_gap:.1f}mm, "
            f"too tight for the {bundle_diameter}mm bundle to press in: "
            f"keep it under {channel - bundle_diameter * 0.7:.1f}",
            param="lip_overhang",
        )
    if holder_width < screw_hole_width + 8.0:
        reject(
            f"holder_width {holder_width} leaves less than 4mm of plastic beside "
            f"the {screw_hole_width}mm screw hole: raise it above {screw_hole_width + 8.0:.1f}",
            param="holder_width",
        )

    floor = hook_thickness
    channel_bottom = floor
    channel_top = channel_bottom + channel
    arm_inner = back_thickness + channel
    arm_outer = arm_inner + hook_thickness
    lip_top = channel_top + lip_overhang  # 45 degree underside, one facet system
    arm_tip = lip_top + 2.5  # short vertical tip so both its edges can chamfer

    # Screw sits above the arm so a driver reaches it straight on.
    screw_z = arm_tip + 3.5
    top = screw_z + 6.5  # a fastener diameter of wall above the loaded bore

    profile = [
        (0.0, 0.0),
        (arm_outer, 0.0),
        (arm_outer, arm_tip),
        (arm_inner - lip_overhang, arm_tip),
    ]
    if lip_overhang > 0.0:
        profile += [
            (arm_inner - lip_overhang, lip_top),
            (arm_inner, channel_top),  # 45 degree underside over the channel
        ]
    profile += [
        (arm_inner, channel_bottom),
        (back_thickness, channel_bottom),
        (back_thickness, top),
        (0.0, top),
    ]
    face = Plane.XZ * make_face(Polyline(*profile, close=True))
    body = extrude(face, amount=holder_width / 2, both=True)

    # 3mm inside-corner relief at both channel-floor junctions: the loaded corners,
    # and together they seat the round bundle like a V-block.
    relief = min(3.0, channel / 2 - 0.6)  # the two seats must not meet mid-floor
    body = chamfer(
        body.edges()
        .filter_by(Axis.Y)
        .filter_by(
            lambda e: abs(e.bounding_box().min.Z - channel_bottom) < 0.01
            and back_thickness - 0.01 < e.bounding_box().min.X < arm_inner + 0.01
        ),
        relief,
    )

    body -= Pos(back_thickness / 2, 0, screw_z) * Cylinder(
        screw_hole_width / 2, back_thickness, rotation=(0, 90, 0)
    )

    if draft:
        return body

    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > 0.01
        and e.bounding_box().max.X > 0.01
        and e not in concave
    )
    return polish(body, keep, 1.0)
