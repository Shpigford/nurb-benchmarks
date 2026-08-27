"""Replacement knob for the measured D-shaped valve stem."""

from math import cos, pi, sin

from nurb import *


_SHAFT_DIAMETER = float(measured("shaft_diameter"))
_SHAFT_ACROSS_FLAT = float(measured("shaft_across_flat"))


@part
def valve_knob(
    shaft_diameter=_SHAFT_DIAMETER,
    shaft_across_flat=_SHAFT_ACROSS_FLAT,
):
    """A support-free, six-lobed valve knob with a torque-driving D socket.

    shaft_diameter: diameter of the round portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter for a D-shaft socket",
            param="shaft_across_flat",
        )

    knob_height = 16.0
    body_radius = 14.5
    lobe_radius = 3.0
    lobe_center_radius = 16.0
    bore_clearance = 0.6
    bottom_thickness = 2.5
    polish_size = 1.0

    # The central disc guarantees a 29mm minimum grip width.  Six overlapping
    # lobes extend the reach without making the whole knob a solid 38mm disc.
    body = Cylinder(
        body_radius,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for index in range(6):
        angle = index * pi / 3.0
        lobe = Pos(
            lobe_center_radius * cos(angle),
            lobe_center_radius * sin(angle),
            0,
        ) * Cylinder(
            lobe_radius,
            knob_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        body = body + lobe

    # Polish only the outside top perimeter.  The bottom stays fully seated on
    # the bed, and the socket is cut after polishing so its fit edges stay sharp.
    top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > knob_height - 0.01
    )
    body = polish(body, top_edges, polish_size)

    # Make a D-shaped negative by clipping a round prism at the +X flat.  For a
    # D shaft, across-flat = radius + flat_x, so flat_x is derived from both
    # measured dimensions rather than from a guessed notch depth.
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    bore_depth = knob_height - bottom_thickness
    bore_bottom_z = bottom_thickness

    round_bore = Pos(0, 0, bore_bottom_z) * Cylinder(
        bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    clip_width = 4.0 * bore_radius
    clip = Pos(bore_flat_x - clip_width / 2.0, 0, bore_bottom_z) * Box(
        clip_width,
        clip_width,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    d_socket = round_bore & clip

    return body - d_socket
