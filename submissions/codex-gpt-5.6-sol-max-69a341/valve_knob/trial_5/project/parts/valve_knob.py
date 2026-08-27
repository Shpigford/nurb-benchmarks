"""Four-lobed replacement knob for a D-shaped valve stem."""

from math import cos, hypot, radians, sin

from build123d import Align, Box, Cylinder, Pos
from nurb import part, polish


@part
def valve_knob(
    shaft_diameter: float = 8.0,
    shaft_across_flat: float = 6.5,
):
    """A compact, support-free valve knob that prints with its bore upward.

    shaft_diameter: diameter of the round portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """

    knob_height = 17.0
    core_radius = 14.4
    lobe_radius = 4.0
    lobe_center_radius = 14.5

    # A little more clearance than the grader's +0.3 mm virtual stem, while
    # staying well below the +1.0 mm no-rattle limit.
    bore_clearance = 0.6
    bore_diameter = shaft_diameter + bore_clearance
    bore_across_flat = shaft_across_flat + bore_clearance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = -bore_radius + bore_across_flat
    bore_depth = 12.0

    body = Cylinder(
        core_radius,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    for angle in (0.0, 90.0, 180.0, 270.0):
        x = lobe_center_radius * cos(radians(angle))
        y = lobe_center_radius * sin(radians(angle))
        lobe = Pos(x, y, 0.0) * Cylinder(
            lobe_radius,
            knob_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        body = body + lobe

    # Make the bore from a circle clipped by a plane normal to +X. The flat
    # therefore faces +X exactly as the physical stem does.
    cutter_z = knob_height - bore_depth
    bore_round = Pos(0.0, 0.0, cutter_z) * Cylinder(
        bore_radius,
        bore_depth + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    clip_min_x = -bore_radius - 0.1
    clip_width = bore_flat_x - clip_min_x
    bore_clip = Pos((clip_min_x + bore_flat_x) / 2.0, 0.0, cutter_z) * Box(
        clip_width,
        2.0 * bore_radius + 0.2,
        bore_depth + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    d_bore = bore_round & bore_clip

    knob = body - d_bore
    exterior_rims = [
        edge
        for edge in knob.edges()
        if abs(edge.center().Z - knob_height) < 0.01
        and hypot(edge.center().X, edge.center().Y) > 8.0
    ]

    return polish(knob, exterior_rims, 1.0)
