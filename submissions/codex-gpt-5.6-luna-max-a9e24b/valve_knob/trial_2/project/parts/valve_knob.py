from math import cos, pi, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    height=14.0,
    knob_radius=15.0,
    lobe_radius=4.5,
    fit_clearance=0.7,
    floor_thickness=2.5,
    draft=False,
):
    """A six-lobed replacement knob for the measured D-shaped valve stem.

    shaft_diameter: round diameter of the valve stem
    shaft_across_flat: stem width from its round side to its flat
    height: overall knob height from the print bed
    knob_radius: radius of the central grip disk
    lobe_radius: radius of each wet-hand grip lobe
    fit_clearance: added clearance across both measured bore dimensions
    floor_thickness: material left below the blind stem socket
    """
    if shaft_diameter <= 0 or shaft_across_flat <= 0:
        reject("shaft dimensions must be positive", param="shaft_diameter")
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter for a D shaft",
            param="shaft_across_flat",
        )
    if height <= floor_thickness + 10.0:
        reject(
            "height must leave a stem socket at least 10mm deep above the floor",
            param="height",
        )

    bore_diameter = shaft_diameter + fit_clearance
    bore_across_flat = shaft_across_flat + fit_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius

    body = Cylinder(
        knob_radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for index in range(6):
        angle = index * pi / 3.0
        lobe_center = knob_radius - 1.0
        body = body + (
            Pos(lobe_center * cos(angle), lobe_center * sin(angle), 0)
            * Cylinder(
                lobe_radius,
                height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        )

    if draft:
        polished_body = body
    else:
        bed = body.bounding_box().min.Z
        top_edges = body.edges().filter_by(
            lambda edge: edge.bounding_box().min.Z > bed
        )
        polished_body = polish(body, top_edges, 1.0)

    socket_floor = floor_thickness
    socket_depth = height - socket_floor
    socket_circle = Pos(0, 0, socket_floor) * Cylinder(
        bore_radius,
        socket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    clip_width = 100.0
    socket_clip = Pos(
        (bore_flat_x - clip_width) / 2.0,
        0,
        socket_floor,
    ) * Box(
        bore_flat_x + clip_width,
        clip_width,
        socket_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    d_socket = socket_circle & socket_clip

    return polished_body - d_socket
