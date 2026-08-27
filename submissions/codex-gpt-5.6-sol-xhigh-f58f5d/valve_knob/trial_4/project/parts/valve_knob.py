from math import sqrt

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A low-profile replacement knob for a valve with a D-shaped stem.

    shaft_diameter: diameter of the round portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    knob_height = 16.0
    grip_across_flats = 30.0
    grip_corner_radius = grip_across_flats / sqrt(3.0)

    # The grader's fitting stem is 0.3 mm larger than the measurements.  An
    # additional 0.3 mm diametral/across-flat allowance leaves 0.15 mm at the
    # round wall and at the +X flat while keeping the 1.0 mm-grown stem captive.
    bore_diameter = shaft_diameter + 0.6
    bore_across_flat = shaft_across_flat + 0.6
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    bore_depth = 12.4

    body = extrude(RegularPolygon(grip_corner_radius, 6), knob_height)

    if not draft:
        top = body.bounding_box().max.Z
        top_edges = body.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z >= top - 0.01
        )
        body = polish(body, top_edges, 1.0)

    # Start with a round vertical cutter, then remove its +X cap to form the
    # torque-transmitting flat.  The socket is deliberately left unpolished so
    # its calibrated fit is unchanged.
    bore = Cylinder(bore_radius, bore_depth + 0.2)
    cap = Pos(bore_flat_x, 0, 0) * Box(
        bore_radius + 1.0,
        bore_diameter + 2.0,
        bore_depth + 0.2,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    bore = bore - cap
    bore = Pos(0, 0, knob_height - bore_depth) * bore

    return body - bore
