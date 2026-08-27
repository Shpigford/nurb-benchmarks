from math import cos, radians, sin

from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A support-free lobed knob for a D-shaped valve stem.

    shaft_diameter: full diameter of the valve's D-shaped stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    if shaft_across_flat >= shaft_diameter:
        reject(
            "shaft_across_flat must be smaller than shaft_diameter for a D-shaft",
            param="shaft_across_flat",
        )
    if shaft_across_flat <= shaft_diameter / 2:
        reject(
            "shaft_across_flat must be more than half shaft_diameter",
            param="shaft_across_flat",
        )

    knob_height = 15.0
    bore_depth = 12.0

    # This 0.6 mm diametral allowance clears the +0.3 mm fit gauge while
    # remaining well inside the +1.0 mm no-rattle gauge.
    bore_diameter = shaft_diameter + 0.6
    bore_across_flat = shaft_across_flat + 0.6
    bore_radius = bore_diameter / 2
    bore_flat_x = bore_across_flat - bore_radius

    # A 28 mm circular core guarantees the minimum grip width. Four broad
    # lobes extend the reach to 17 mm for wet-hand leverage without a bulky
    # full-diameter body.
    core_radius = 14.0
    lobe_radius = 4.0
    lobe_center_radius = 13.0
    outer_profile = Circle(core_radius)
    for angle in (0, 90, 180, 270):
        x = lobe_center_radius * cos(radians(angle))
        y = lobe_center_radius * sin(radians(angle))
        outer_profile = outer_profile + Pos(x, y, 0) * Circle(lobe_radius)

    body = extrude(outer_profile, amount=knob_height)

    # Intersecting the circle with a half-plane preserves an exact circular
    # wall and puts the torque-transmitting flat on +X.
    clip_width = bore_flat_x + bore_radius
    bore_clip = Pos(-bore_radius, 0, 0) * Rectangle(
        clip_width,
        bore_diameter,
        align=(Align.MIN, Align.CENTER),
    )
    bore_profile = Circle(bore_radius) & bore_clip
    bore = Pos(0, 0, knob_height - bore_depth) * extrude(
        bore_profile,
        amount=bore_depth + 0.2,
    )
    knob = body - bore

    if draft:
        return knob

    # Chamfer only the exposed outer top rim. The bed face and the bore's
    # fit-critical mouth stay dimensionally exact.
    outer_top_edges = knob.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > knob_height - 0.01
        and edge.center().X * edge.center().X + edge.center().Y * edge.center().Y
        > 100.0
    )
    return polish(knob, outer_top_edges, 1.0)
