from nurb import *


@part
def valve_knob(
    shaft_diameter=float(measured("shaft_diameter")),
    shaft_across_flat=float(measured("shaft_across_flat")),
    grip_length=40.0,
    grip_width=30.0,
    knob_height=14.0,
    socket_depth=11.5,
    shaft_clearance=0.5,
    draft=False,
):
    """Oval valve knob, printed closed face down with its D socket facing up.

    shaft_diameter: measured diameter of the valve stem's round portion.
    shaft_across_flat: distance from the stem's flat to its opposite round side.
    grip_length: overall length of the oval hand grip.
    grip_width: overall width of the oval hand grip.
    knob_height: height from the print bed to the socket mouth.
    socket_depth: depth of the upward opening socket.
    shaft_clearance: extra opening size on diameter and across the flat.
    """
    if shaft_diameter <= 0 or not shaft_diameter / 2 < shaft_across_flat < shaft_diameter:
        reject("The stem flat must lie between the center and the round edge.",
               param="shaft_across_flat")
    if shaft_clearance <= 0:
        reject("Use positive clearance for the stem socket.", param="shaft_clearance")
    if socket_depth <= 0 or knob_height - socket_depth < 2.5:
        reject("Leave at least 2.5 mm of solid floor below the socket.",
               param="knob_height")
    bore_radius = (shaft_diameter + shaft_clearance) / 2
    flat_x = shaft_across_flat + shaft_clearance - bore_radius
    if min(grip_length, grip_width) < 2 * bore_radius + 6:
        reject("The grip must leave at least 3 mm around the socket.", param="grip_width")

    body = extrude(Ellipse(grip_length / 2, grip_width / 2), amount=knob_height)
    if not draft:
        # Only the exposed outside rim is dressed; bed and socket retain their dimensions.
        top_rim = body.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z > knob_height - 0.001
        )
        body = polish(body, top_rim, 1.0)

    # Clip a true circle at +X. Across-flat is measured from -radius to this plane.
    socket_round = Cylinder(
        bore_radius, socket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    socket_halfspace = Pos(-bore_radius, -bore_radius, 0) * Box(
        bore_radius + flat_x, 2 * bore_radius, socket_depth + 1.0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    socket = Pos(0, 0, knob_height - socket_depth) * (socket_round & socket_halfspace)
    return body - socket
