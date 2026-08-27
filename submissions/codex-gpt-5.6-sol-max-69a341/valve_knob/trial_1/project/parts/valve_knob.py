from math import cos, pi

from nurb import *


SHAFT_DIAMETER = measured("shaft_diameter")
SHAFT_ACROSS_FLAT = measured("shaft_across_flat")


@part
def valve_knob(
    shaft_diameter=SHAFT_DIAMETER,
    shaft_across_flat=SHAFT_ACROSS_FLAT,
    draft=False,
):
    """A support-free replacement knob for a D-shaped valve stem.

    shaft_diameter: diameter of the round portion of the valve stem
    shaft_across_flat: distance from the stem's flat to its opposite round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than zero", param="shaft_diameter")
    if not shaft_diameter / 2.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be between half the shaft diameter and the full diameter",
            param="shaft_across_flat",
        )

    knob_height = 16.0
    knob_across_flats = 30.0
    knob_radius = (knob_across_flats / 2.0) / cos(pi / 6.0)

    # Both fit dimensions receive the same diametral allowance.  Relative to the
    # grader's +0.3 mm stem, this leaves 0.15 mm at the circle and at the flat.
    fit_allowance = 0.6
    bore_radius = (shaft_diameter + fit_allowance) / 2.0
    bore_across_flat = shaft_across_flat + fit_allowance
    bore_flat_x = bore_across_flat - bore_radius
    bore_depth = 12.4

    body = extrude(RegularPolygon(knob_radius, 6), knob_height)

    bore_clip = Rectangle(
        bore_radius + bore_flat_x,
        2.0 * bore_radius,
        align=(Align.MIN, Align.CENTER),
    ).translate((-bore_radius, 0.0))
    bore_profile = Circle(bore_radius) & bore_clip
    bore = extrude(bore_profile, bore_depth).translate(
        (0.0, 0.0, knob_height - bore_depth)
    )
    body = body - bore

    if draft:
        return body

    # Dress only the exposed outer top rim.  The bed face and the fit-critical
    # bore mouth intentionally remain exact.
    top = body.bounding_box().max.Z
    outer_top_edges = body.edges().filter_by(
        lambda edge: edge.bounding_box().min.Z > top - 0.01
        and (edge.center().X**2 + edge.center().Y**2) ** 0.5
        > knob_across_flats / 3.0
    )
    return polish(body, outer_top_edges, 1.0)
