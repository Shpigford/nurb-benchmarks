from math import cos, pi, sin

from nurb import *


_MEASURED_SHAFT_DIAMETER = measured("shaft_diameter")
_MEASURED_SHAFT_ACROSS_FLAT = measured("shaft_across_flat")


@part
def valve_knob(
    shaft_diameter=_MEASURED_SHAFT_DIAMETER,
    shaft_across_flat=_MEASURED_SHAFT_ACROSS_FLAT,
    draft=False,
):
    """Replacement knob for the measured D-shaped valve stem.

    shaft_diameter: diameter of the round part of the valve stem
    shaft_across_flat: distance from the stem flat to the opposite round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if shaft_across_flat <= 0.0 or shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be positive and smaller than shaft_diameter",
            param="shaft_across_flat",
        )

    knob_height = 16.0
    grip_radius = 14.2
    lobe_radius = 3.2
    lobe_center_radius = 15.6
    socket_depth = 11.0
    socket_clearance = 0.6

    # The body is a round core with six overlapping round lobes.  This keeps
    # the minimum grip diameter above 28 mm while giving wet hands a positive
    # set of torque surfaces without spending the volume of a solid 37 mm disk.
    body = Cylinder(
        grip_radius,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for index in range(6):
        angle = index * pi / 3.0
        lobe = Pos(
            lobe_center_radius * cos(angle),
            lobe_center_radius * sin(angle),
            0.0,
        ) * Cylinder(
            lobe_radius,
            knob_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        body = body + lobe

    # A D socket is a round bore clipped by a flat on +X.  Deriving its
    # diameter and flat position independently from both shaft measurements
    # preserves the D relationship when either exposed parameter changes.
    socket_diameter = shaft_diameter + socket_clearance
    socket_across_flat = shaft_across_flat + socket_clearance
    socket_radius = socket_diameter / 2.0
    socket_flat_x = socket_across_flat - socket_radius

    socket_cylinder = Pos(0.0, 0.0, knob_height - socket_depth) * Cylinder(
        socket_radius,
        socket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    window_width = 2.0 * socket_radius + 4.0
    socket_window = Pos(
        socket_flat_x - window_width / 2.0,
        0.0,
        knob_height - socket_depth,
    ) * Box(
        window_width,
        window_width,
        socket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    d_socket = socket_cylinder & socket_window
    result = body - d_socket

    if draft:
        return result

    # Keep the bed face and the fit-critical socket rim sharp.  The exposed
    # upper grip rim gets the standard 1 mm print-friendly chamfer.
    top_edges = result.edges().filter_by(
        lambda edge: (
            abs(edge.bounding_box().min.Z - knob_height) < 1e-6
            and abs(edge.bounding_box().max.Z - knob_height) < 1e-6
            and edge.bounding_box().min.X < grip_radius + lobe_radius
            and edge.bounding_box().max.X > -grip_radius - lobe_radius
        )
    )
    return polish(result, top_edges, 1.0)
