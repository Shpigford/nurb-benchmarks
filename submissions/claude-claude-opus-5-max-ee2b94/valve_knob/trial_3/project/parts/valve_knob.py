from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    socket_clearance=0.65,
    socket_depth=11.5,
    knob_height=14.0,
    grip_width=29.2,
    lobe_reach=17.6,
    lobe_round=6.0,
    lobe_count=4,
    valley_round=2.5,
    chamfer_size=1.0,
    draft=False,
):
    """A replacement knob that drops onto the valve's D-shaped stem.

    shaft_diameter: how wide the valve stem is across its round side
    shaft_across_flat: how wide the stem is from its flat face to the round side opposite
    socket_clearance: how much roomier than the stem the socket is cut, so it slips on by hand
    socket_depth: how far down into the knob the stem reaches
    knob_height: how tall the knob stands
    grip_width: how wide the knob measures across its narrowest, valley to valley
    lobe_reach: how far a finger lobe stands out from the centre
    lobe_round: how fat and round each finger lobe is
    lobe_count: how many finger lobes go round the knob
    valley_round: how softly the valleys between the lobes are rounded
    chamfer_size: the bevel taken off the top rim
    """
    # The socket is the whole point of the part, so it is worked out first and
    # everything else is sized to leave room around it.
    socket_radius = (shaft_diameter + socket_clearance) / 2.0
    flat_offset = (shaft_across_flat + socket_clearance) - socket_radius
    core_radius = grip_width / 2.0
    floor = knob_height - socket_depth

    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} leaves no flat on a {shaft_diameter}mm "
            "stem, and a round socket spins instead of turning the valve: it has to be "
            "smaller than shaft_diameter",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter / 2.0:
        reject(
            f"shaft_across_flat {shaft_across_flat} cuts the flat past the centre of a "
            f"{shaft_diameter}mm stem, which is not a D-shaft: raise it above "
            f"{shaft_diameter / 2.0:.2f}",
            param="shaft_across_flat",
        )
    if floor < 2.0:
        reject(
            f"socket_depth {socket_depth} leaves a {floor:.2f}mm floor under the stem, "
            f"under the 2mm minimum wall: lower it below {knob_height - 2.0:.2f} or raise "
            "knob_height",
            param="socket_depth",
        )
    if core_radius - socket_radius < 3.0:
        reject(
            f"grip_width {grip_width} leaves {core_radius - socket_radius:.2f}mm of wall "
            f"round the socket: raise it above {2.0 * (socket_radius + 3.0):.2f}",
            param="grip_width",
        )
    if lobe_reach <= core_radius + valley_round:
        reject(
            f"lobe_reach {lobe_reach} does not stand out past the {core_radius:.2f}mm "
            f"waist far enough to grip: raise it above {core_radius + valley_round:.2f}",
            param="lobe_reach",
        )
    if lobe_count < 3:
        reject(
            f"lobe_count {lobe_count} gives a hand too little to turn against, and at 0 "
            "the outline is a bare circle with nothing to round: raise it to 3 or more",
            param="lobe_count",
        )

    # Outline: a waist circle at the narrowest grip dimension with the lobes swung out
    # past it. Both radii are set independently, so the reach past the waist is a
    # deliberate number rather than whatever a polygon happened to leave.
    lobe_centre = lobe_reach - lobe_round
    outline = Circle(core_radius)
    lobe = Pos(lobe_centre, 0.0) * Circle(lobe_round)
    for i in range(lobe_count):
        outline += Rot(0.0, 0.0, 360.0 * i / lobe_count) * lobe
    # The union leaves a crease where each lobe meets the waist. Rounding it in the
    # outline keeps the top rim smooth all the way round, so its chamfer lands as one
    # continuous band instead of mitring itself into slivers at every crease.
    outline = fillet(outline.vertices(), valley_round)

    body = extrude(outline, knob_height)

    # The socket: a circle with the stem's flat facing +X, cut down from the top face.
    # It over-runs the top so the mouth is a clean edge rather than a coincident face.
    flat_cut = Pos(flat_offset - socket_radius, 0.0) * Rectangle(
        2.0 * socket_radius, 4.0 * socket_radius
    )
    socket = Circle(socket_radius) & flat_cut
    body -= Pos(0.0, 0.0, floor) * extrude(socket, socket_depth + 1.0)

    if draft:
        return body

    # Polish the top rim only. The bottom outline lies in the bed face, the socket mouth
    # is the mating geometry, and the outline has no vertical corners left to take.
    top = body.bounding_box().max.Z
    reach = (socket_radius + core_radius) / 2.0
    rim = body.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Z - top) < 1e-4
        and abs(e.bounding_box().max.Z - top) < 1e-4
        and (e.center().X**2 + e.center().Y**2) ** 0.5 > reach
    )
    return polish(body, rim, chamfer_size)
