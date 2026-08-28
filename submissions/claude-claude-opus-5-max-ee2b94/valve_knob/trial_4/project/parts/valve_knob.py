from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    bore_clearance=0.6,
    bore_depth=12.5,
    knob_height=15.0,
    knob_width=36.0,
    grip_count=5,
    grip_depth=5.0,
    grip_radius=8.0,
    chamfer_size=1.0,
    draft=False,
):
    """A replacement handle for a D-shaft valve stem.

    shaft_diameter: how wide the valve's stem measures across its round side
    shaft_across_flat: how thick the stem measures from its flat to the round side
    bore_clearance: how much wider than the stem the socket is cut, so it slides on
    bore_depth: how far down the socket goes from the top face
    knob_height: how tall the knob stands
    knob_width: how far across the knob measures at its widest, lobe to lobe
    grip_count: how many finger scallops go round the rim, kept odd so each
        scallop faces a lobe and the knob stays wide whichever way you grab it
    grip_depth: how far each scallop bites into the rim
    grip_radius: how round each scallop is, roughly a fingertip
    chamfer_size: how big the chamfer on the top rim is
    """
    peak = knob_width / 2.0
    valley = peak - grip_depth

    # The socket is the stem's D-profile grown by the fit clearance on both of the
    # dimensions that were measured: the round side and the flat.
    bore_radius = (shaft_diameter + bore_clearance) / 2.0
    flat_offset = (shaft_across_flat + bore_clearance) - bore_radius

    # The flat is what carries the torque, and its depth is the difference between
    # the two measurements: the clearance moves the flat and the round side together.
    flat_depth = shaft_diameter - shaft_across_flat
    if flat_depth < 0.8:
        reject(
            f"shaft_across_flat {shaft_across_flat} leaves a {flat_depth:.1f}mm flat "
            f"on a {shaft_diameter}mm stem, which is under two bead widths of drive: "
            f"the knob would round off and spin. Measure from the flat to the round "
            f"side again and expect it under {shaft_diameter - 0.8:.1f}",
            param="shaft_across_flat",
        )
    if 2.0 * bore_radius < 2.0:
        reject(
            f"shaft_diameter {shaft_diameter} makes a "
            f"{2.0 * bore_radius:.1f}mm socket, and a bore under 2mm prints as a "
            f"smear or closes outright",
            param="shaft_diameter",
        )
    if valley - bore_radius < 2.0:
        reject(
            f"knob_width {knob_width} leaves {valley - bore_radius:.1f}mm of wall "
            f"between the socket and the bottom of a scallop: raise knob_width "
            f"above {2.0 * (bore_radius + 2.0 + grip_depth):.1f} or cut grip_depth",
            param="knob_width",
        )

    # Odd lobe count on purpose: every scallop faces a lobe across the knob, so the
    # width across stays full however the hand grabs it.
    outline = Circle(peak)
    for i in range(grip_count):
        angle = 360.0 * (i + 0.5) / grip_count
        centre = Rot(0.0, 0.0, angle) * Pos(valley + grip_radius, 0.0, 0.0)
        outline -= centre * Circle(grip_radius)
    body = extrude(outline, knob_height)

    # The flat faces +X, so a lobe stands behind it where the torque is carried.
    socket = Circle(bore_radius) - Pos(
        flat_offset + bore_radius, 0.0
    ) * Rectangle(2.0 * bore_radius, 2.0 * bore_radius + 2.0)
    body -= Pos(0.0, 0.0, knob_height - bore_depth) * extrude(socket, bore_depth + 1.0)

    if draft:
        return body

    # Polish the top rim only. The bottom rim lies in the bed face, the scallop
    # junctions are concave, and the socket mouth is what slides onto the stem.
    top = body.bounding_box().max.Z
    reach = (bore_radius + valley) / 2.0

    def top_rim(e):
        bb = e.bounding_box()
        if abs(bb.min.Z - top) > 1e-6 or abs(bb.max.Z - top) > 1e-6:
            return False
        return max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y)) > reach

    return polish(body, body.edges().filter_by(top_rim), chamfer_size)
