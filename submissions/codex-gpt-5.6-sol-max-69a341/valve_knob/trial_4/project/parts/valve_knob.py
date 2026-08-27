from nurb import *


@part
def valve_knob(
    shaft_diameter=measured("shaft_diameter"),
    shaft_across_flat=measured("shaft_across_flat"),
    draft=False,
):
    """A compact square replacement knob for a D-shaped valve stem.

    shaft_diameter: the full round diameter of the valve stem
    shaft_across_flat: the distance from the stem's flat to its round side
    """
    if shaft_diameter <= 0.0:
        reject("shaft_diameter must be greater than 0mm", param="shaft_diameter")
    if not shaft_diameter / 2.0 < shaft_across_flat < shaft_diameter:
        reject(
            "shaft_across_flat must be between half of shaft_diameter and its full diameter",
            param="shaft_across_flat",
        )

    knob_width = 30.0
    knob_height = 15.0
    bore_depth = 12.5

    # Adding the same diametral allowance to both D-shaft measurements keeps the
    # flat in the correct +X orientation while providing controlled print fit.
    fit_allowance = 0.6
    bore_diameter = shaft_diameter + fit_allowance
    bore_across_flat = shaft_across_flat + fit_allowance
    bore_radius = bore_diameter / 2.0
    bore_flat_x = bore_across_flat - bore_radius
    bore_bottom = knob_height - bore_depth

    body = Box(
        knob_width,
        knob_width,
        knob_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    round_bore = Pos(0.0, 0.0, bore_bottom) * Cylinder(
        bore_radius,
        bore_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    flat_limit = Pos(bore_flat_x, 0.0, bore_bottom) * Box(
        bore_radius * 4.0,
        bore_radius * 4.0,
        bore_depth,
        align=(Align.MAX, Align.CENTER, Align.MIN),
    )
    d_bore = round_bore & flat_limit
    knob = body - d_bore

    if draft:
        return knob

    # Only the four handled vertical corners are polished. The bed face and the
    # fit-critical bore remain dimensionally exact and free of lead-in chamfers.
    vertical_corners = knob.edges().filter_by(
        lambda edge: edge.bounding_box().max.Z - edge.bounding_box().min.Z
        > knob_height - 0.1
    )
    return polish(knob, vertical_corners, 1.0)
