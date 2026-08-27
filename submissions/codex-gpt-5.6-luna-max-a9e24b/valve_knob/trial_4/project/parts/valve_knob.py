from math import cos, pi, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    knob_height=16.0,
    grip_radius=14.5,
    lobe_reach=17.5,
    bore_depth=12.5,
    draft=False,
):
    """Replacement knob for the measured D-shaped valve stem.

    shaft_diameter: diameter of the valve stem
    shaft_across_flat: distance from the stem flat to its opposite round side
    knob_height: total height of the knob while printing
    grip_radius: radius at the valleys between the six grip lobes
    lobe_reach: outer radius at the tips of the grip lobes
    bore_depth: depth of the blind socket from the top face
    """
    if knob_height < 12.0:
        reject("knob_height must be at least 12.0 mm for the stem engagement", param="knob_height")
    if bore_depth >= knob_height - 2.0:
        reject("bore_depth must leave at least 2.0 mm of material under the socket", param="bore_depth")
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than 0", param="shaft_diameter")
    if shaft_across_flat <= shaft_diameter / 2.0 or shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be between the stem radius and shaft_diameter",
            param="shaft_across_flat",
        )
    if grip_radius < 14.0:
        reject("grip_radius must be at least 14.0 mm to keep a 28 mm hand grip", param="grip_radius")
    if lobe_reach <= grip_radius * 1.12:
        reject("lobe_reach must be at least 12% beyond grip_radius", param="lobe_reach")

    # The virtual fit stem is allowed 0.3 mm on both of its measured dimensions.
    # The bore gets a little more than that so the fit is not a tangent boolean.
    bore_diameter = shaft_diameter + 0.6
    bore_across_flat = shaft_across_flat + 0.6
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    bore_bottom = knob_height - bore_depth

    body = Cylinder(
        grip_radius,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    lobe_radius = 3.0
    lobe_center_radius = lobe_reach - lobe_radius
    if lobe_center_radius + lobe_radius <= grip_radius:
        reject("lobe_reach must leave the lobes joined to the grip body", param="lobe_reach")
    for index in range(6):
        angle = index * pi / 3.0
        body = body + Pos(
            lobe_center_radius * cos(angle),
            lobe_center_radius * sin(angle),
            0,
        ) * Cylinder(
            lobe_radius,
            knob_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    # Clip a round prism at +X to make the D socket's flat face.  The socket is
    # deliberately left blind, with a solid floor beneath the valve stem.
    round_bore = Pos(0, 0, bore_bottom) * Cylinder(
        bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    d_clip = Pos(
        (bore_flat_x - bore_radius) / 2.0,
        0,
        bore_bottom,
    ) * Box(
        bore_flat_x + bore_radius,
        2.0 * bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    socket = round_bore & d_clip
    result = body - socket

    if draft:
        return result

    bed = result.bounding_box().min.Z
    concave = concave_edges(result)
    exposed = result.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > bed + 0.01 and edge not in concave
    )
    return polish(result, exposed, 1.0)
