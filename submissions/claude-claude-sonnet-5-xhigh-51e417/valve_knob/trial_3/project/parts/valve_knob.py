from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    bore_clearance=0.65,
    bore_depth=12.5,
    base_thickness=3.0,
    grip_width=29.2,
    grip_length=36.5,
    draft=False,
):
    """
    shaft_diameter: the valve stem's diameter, straight across
    shaft_across_flat: the valve stem's narrower dimension, across its ground flat
    bore_clearance: how much bigger the bore is than the stem, added to both dimensions
    bore_depth: how deep the bore is cut down from the top face
    base_thickness: solid material left below the bore, down to the bed
    grip_width: how wide the knob is at its narrowest, for wet hands to grip
    grip_length: how wide the knob is at its widest, across its long axis
    """
    if not (0 < shaft_across_flat < shaft_diameter):
        reject(
            f"shaft_across_flat {shaft_across_flat} must sit between 0 and shaft_diameter {shaft_diameter}",
            param="shaft_across_flat",
        )
    if bore_depth < 10.0:
        reject(
            f"bore_depth {bore_depth} is under the 10mm the stem needs to seat; raise it above 10.0",
            param="bore_depth",
        )
    if grip_length <= grip_width:
        reject(
            f"grip_length {grip_length} must exceed grip_width {grip_width} or the knob has no grip lobes",
            param="grip_length",
        )

    height = bore_depth + base_thickness
    a = grip_length / 2
    b = grip_width / 2

    body = extrude(Ellipse(a, b), height)

    # The bore is a D-shape: a circle with the +X cap sliced off at the flat,
    # sized to the stem plus clearance on both the round and flat dimensions.
    bore_radius = (shaft_diameter + bore_clearance) / 2
    bore_across_flat = shaft_across_flat + bore_clearance
    flat_x = bore_across_flat - bore_radius
    cap_width = bore_radius + 2 - flat_x
    cap = Pos(flat_x + cap_width / 2, 0) * Rectangle(cap_width, 2 * bore_radius + 4)
    bore_profile = Circle(bore_radius) - cap
    bore = Pos(0, 0, height - bore_depth) * extrude(bore_profile, bore_depth)

    body = body - bore

    if draft:
        return body

    top = height
    concave = concave_edges(body)
    keep = body.edges().filter_by(
        lambda e: e.bounding_box().min.Z > top - 1e-3
        and e.bounding_box().max.Z > top - 1e-3
        and e.bounding_box().max.X > b - 1.0
        and e not in concave
    )
    return polish(body, keep, 1.0)
