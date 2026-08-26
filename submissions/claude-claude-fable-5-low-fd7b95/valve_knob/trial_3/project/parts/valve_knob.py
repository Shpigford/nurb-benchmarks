from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    grip_width=28.5,
    knob_height=15.0,
    bore_clearance=0.6,
    draft=False,
):
    """A replacement knob for the valve's D-shaft stem, printed bore-up.

    shaft_diameter: the stem's full diameter across the round part
    shaft_across_flat: the stem's width from its flat side to the round side
    grip_width: how wide the hex grip is across its flats
    knob_height: how tall the knob stands
    bore_clearance: extra room in the socket so the knob slides onto the stem
    """
    bore_r = (shaft_diameter + bore_clearance) / 2
    flat_x = (shaft_across_flat + bore_clearance) - bore_r
    bore_depth = 12.4

    if bore_r + 3.0 > grip_width / 2:
        reject(
            "grip_width leaves under 3mm of wall around the bore: "
            f"raise it above {2 * (bore_r + 3.0):.1f}",
            param="grip_width",
        )

    # Hex grip: across-flats = grip_width, corners reach 15.5% past the flats.
    corner_r = grip_width / (3**0.5)
    body = extrude(RegularPolygon(corner_r, 6), knob_height)

    # D-shaped socket, open at the top, flat facing +X.
    d_profile = Circle(bore_r) - Pos(flat_x + bore_r, 0) * Rectangle(
        2 * bore_r, 2 * bore_r + 2
    )
    body -= Pos(0, 0, knob_height - bore_depth) * extrude(d_profile, bore_depth)

    if draft:
        return body

    # Polish everything except the bed-plane edges and the bore's mating mouth.
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().max.Z > 1e-6
        and (e.center().X**2 + e.center().Y**2) ** 0.5 > bore_r + 1.0
    )
    return polish(body, keep, 1.0)
