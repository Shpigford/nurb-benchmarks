from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    bore_clearance=0.3,
    bore_depth=12.5,
    knob_height=15.0,
    grip_diameter=30.0,
    lobe_size=5.0,
    lobe_count=5,
    chamfer_size=1.0,
    draft=False,
):
    """A five-lobed hand knob that replaces the valve's broken handle.

    Prints bore-up, then flips over onto the valve's D-stem in use.

    shaft_diameter: width of the valve stem across its round part
    shaft_across_flat: width of the stem from its flat side to the round side
    bore_clearance: extra gap on each side so the knob slides onto the stem
    bore_depth: how deep the stem socket reaches down from the top face
    knob_height: overall height of the knob
    grip_diameter: width across the knob between the lobes, the narrowest grip
    lobe_size: radius of each grip lobe around the rim
    lobe_count: how many grip lobes around the rim
    chamfer_size: size of the polished edge chamfers
    """
    if shaft_diameter < 3.0:
        reject(
            f"shaft_diameter {shaft_diameter} needs a bore under the 2mm printable "
            "minimum and no valve stem is that thin: re-measure the stem",
            param="shaft_diameter",
        )
    if shaft_across_flat >= shaft_diameter:
        reject(
            f"shaft_across_flat {shaft_across_flat} is not under shaft_diameter "
            f"{shaft_diameter}, so there is no flat for the bore to key on and the "
            "knob would spin free: re-measure the stem",
            param="shaft_across_flat",
        )
    if bore_clearance < 0.1:
        reject(
            f"bore_clearance {bore_clearance} is under the 0.1 bind limit and the "
            "knob would seize on the stem: use 0.1 to 0.5",
            param="bore_clearance",
        )
    if chamfer_size < 0.8:
        reject(
            f"chamfer_size {chamfer_size} is under the 0.8 printable floor: "
            "use 0.8 to 1.5",
            param="chamfer_size",
        )

    bore_radius = shaft_diameter / 2 + bore_clearance
    flat_offset = shaft_across_flat + 2 * bore_clearance - bore_radius
    grip_radius = grip_diameter / 2

    if grip_radius - bore_radius < 2.0:
        reject(
            f"grip_diameter {grip_diameter} leaves under 2mm of wall around the "
            f"{2 * bore_radius:.1f}mm bore: raise it above "
            f"{2 * (bore_radius + 2.0):.1f}",
            param="grip_diameter",
        )
    if knob_height - bore_depth < 2.0:
        reject(
            f"bore_depth {bore_depth} leaves under 2mm of floor in a "
            f"{knob_height}mm tall knob: keep it below {knob_height - 2.0:.1f}",
            param="bore_depth",
        )
    if bore_depth < 5.0:
        reject(
            f"bore_depth {bore_depth} grips under 5mm of stem and would strip "
            "when torqued: use 5 or more",
            param="bore_depth",
        )
    if lobe_count < 3:
        reject(
            "fewer than 3 lobes cannot be gripped evenly all round: use 3 to 7",
            param="lobe_count",
        )
    if not 1.0 <= lobe_size <= grip_radius:
        reject(
            f"lobe_size {lobe_size} is outside 1.0 to {grip_radius:.1f}: smaller "
            "is decoration rather than grip, larger swallows the knob",
            param="lobe_size",
        )

    # Grip: a circle with lobes half-buried in its rim, one lobe centred on +X
    # to match the stem flat's symmetry plane.
    profile = Circle(grip_radius) + (
        PolarLocations(grip_radius - lobe_size / 2, lobe_count) * Circle(lobe_size)
    )
    body = extrude(profile, knob_height)

    # Stem socket: the shaft's D-section grown by the clearance on every side,
    # cut straight down from the top face. The flat faces +X.
    d_section = Circle(bore_radius) - Pos(flat_offset + bore_radius, 0) * Rectangle(
        2 * bore_radius, 3 * bore_radius
    )
    body -= Pos(0, 0, knob_height - bore_depth) * extrude(d_section, bore_depth)

    if draft:
        return body

    # Polish the top rim only: bottom-face edges buy nothing, the lobe valleys
    # are concave, and the bore is fit-critical mating geometry.
    bed = body.bounding_box().min.Z

    def clear_of_bore(edge):
        bb = edge.bounding_box()
        reach = max(
            (x * x + y * y) ** 0.5
            for x in (bb.min.X, bb.max.X)
            for y in (bb.min.Y, bb.max.Y)
        )
        return reach > 1.5 * bore_radius

    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > bed + 1e-4 and clear_of_bore(e)
    )
    return polish(body, keep, chamfer_size)
