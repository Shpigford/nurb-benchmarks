from nurb import *


@part
def valve_knob(shaft_diameter=8.0, shaft_across_flat=6.5,
               knob_width=38.0, knob_depth=29.0, knob_height=14.0,
               socket_depth=11.0, draft=False):
    """Oval valve grip, printed socket up and flipped onto the valve stem.

    shaft_diameter: measured diameter of the round portion of the stem.
    shaft_across_flat: measured distance from the flat to the opposite round side.
    knob_width: longest outside dimension of the oval grip.
    knob_depth: shortest outside dimension of the oval grip.
    knob_height: total height from the flat print base to the socket opening.
    socket_depth: distance the stem enters from the upward socket opening.
    """
    if not 0.0 < shaft_across_flat < shaft_diameter:
        reject("shaft_across_flat must be positive and below shaft_diameter",
               param="shaft_across_flat")
    if socket_depth <= 0.0 or knob_height - socket_depth < 3.0:
        reject("knob_height must leave at least 3 mm below the socket",
               param="knob_height")
    radius = (shaft_diameter + 0.4) / 2.0
    flat_x = shaft_across_flat + 0.4 - radius
    if min(knob_width, knob_depth) / 2.0 - radius < 3.0:
        reject("grip dimensions must leave at least 3 mm around the socket",
               param="knob_depth")

    body = extrude(Ellipse(knob_width / 2.0, knob_depth / 2.0), knob_height)
    if not draft:
        top_rim = body.edges().filter_by(
            lambda e: e.bounding_box().min.Z > knob_height - 0.001)
        body = polish(body, top_rim, 1.0)

    # Intersection clips the round cutter at the stem's +X flat plane.
    floor_z = knob_height - socket_depth
    round_cut = Pos(0, 0, floor_z) * Cylinder(
        radius, socket_depth + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    flat_clip = Pos(-radius - 1.0, 0, floor_z) * Box(
        radius + 1.0 + flat_x, 2.0 * radius + 2.0, socket_depth + 1.0,
        align=(Align.MIN, Align.CENTER, Align.MIN))
    return body - (round_cut & flat_clip)
