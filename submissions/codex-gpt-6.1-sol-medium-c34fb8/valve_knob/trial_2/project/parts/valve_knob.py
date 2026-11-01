from nurb import *


@part
def valve_knob(
    shaft_diameter=8.0,
    shaft_across_flat=6.5,
    grip_width=38.0,
    grip_depth=30.0,
    knob_height=15.0,
    socket_depth=12.4,
    fit_clearance=0.4,
    draft=False,
):
    """An elongated valve knob, printed with its D socket facing upward.

    shaft_diameter: diameter across the round portion of the valve stem.
    shaft_across_flat: distance from the flat to the opposite round side.
    grip_width: length of the oval grip for turning leverage.
    grip_depth: width of the oval grip at its narrowest.
    knob_height: total height of the knob above the print bed.
    socket_depth: depth of the upward opening that receives the stem.
    fit_clearance: extra width in both measured socket dimensions.
    """
    if not 0 < shaft_across_flat < shaft_diameter:
        reject("shaft_across_flat must be between zero and shaft_diameter", param="shaft_across_flat")
    if knob_height - socket_depth < 2.0:
        reject("knob_height must leave at least 2mm below socket_depth", param="knob_height")
    bore_radius = (shaft_diameter + fit_clearance) / 2
    flat_x = shaft_across_flat + fit_clearance - bore_radius
    if min(grip_width, grip_depth) < shaft_diameter + fit_clearance + 6.0:
        reject("grip_depth and grip_width must leave at least 3mm around the socket", param="grip_depth")

    body = extrude(Ellipse(grip_width / 2, grip_depth / 2), amount=knob_height)
    # Intersect the cylinder with a half-space: the retained plane faces +X.
    socket = Pos(0, 0, knob_height - socket_depth) * Cylinder(
        bore_radius, socket_depth + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    half_space = Pos(flat_x - 2 * bore_radius, 0, knob_height - socket_depth) * Box(
        4 * bore_radius, 4 * bore_radius, socket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body = body - (socket & half_space)
    if draft:
        return body
    # Keep all fit faces, the socket lip, and the large bed contact exact.
    exposed_rim = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > knob_height - 0.01
        and edge.length > 2 * max(grip_width, grip_depth)
    )
    return polish(body, exposed_rim, 1.0)
